<?php
  function sign($cn, $csr) {
    $cacert = file_get_contents("/usr/share/openvpn/easy-rsa/2.0/keys/ca.crt");
    $privkey = file_get_contents("/usr/share/openvpn/easy-rsa/2.0/keys/ca.key");
    $usercert = openssl_csr_sign($csr, $cacert, $privkey, 3650);
    openssl_x509_export($usercert, $certout);
    syslog(LOG_INFO, "New certificate issued for $cn:\n" . $certout);
    $fh = fopen("/etc/openvpn/certs/$cn", 'w') or die("Can't open '/etc/openvpn/certs/$cn' file");
    fwrite($fh, $certout);
    fclose($fh);
    return $certout;
  }

  if (getmyuid() == 0) {
    if ($_SERVER['argc'] != 3) {
       echo "php " . $_SERVER['argv'][0] . " <hostname> <csr-filename>\n";
       return;
    }
    $cn = $_SERVER['argv'][1];
    $csr_file = $_SERVER['argv'][2];

    $csr = file_get_contents($csr_file);

    $cert = sign($cn, $csr);

    echo $cert;

    return;
  }

  require_once 'plc_api.php';

  global $plc, $api;

  $error = "";
  if (isset($_POST["csr"])) {
    openlog("sign-csr", LOG_ODELAY, LOG_USER);

    $csr = $_POST["csr"];

    syslog(LOG_INFO, "A request for signing the following CSR for $_SERVER[REMOTE_ADDR]:\n" . $csr);

    $cn = null;
    $subjects = openssl_csr_get_subject($csr);
    if (isset($subjects["CN"])) {
      $cn = $subjects["CN"];
      if (preg_match('/\\.measurement-lab\\.org$/', $cn)) {
        $cn_ip = gethostbyname($cn);
        $client_ip = $_SERVER["REMOTE_ADDR"];
        if (strcmp($cn_ip, $client_ip) == 0) {
          $session = $_REQUEST["session"];
          syslog(LOG_INFO, "Authenticating session with key $session for $_SERVER[REMOTE_ADDR]...");
          $auth = array('AuthMethod' => "session", 'session' => $session);
          $api = new PLCAPI($auth);
          if ($api->AuthCheck() == "1") {
            $cert = sign($cn, $csr);
            header("Content-Type: application/octet-stream");
            header("Content-Disposition: attachment; filename=client.crt");
            echo $cert;
            return;
          } else {
            $error = "Authentication failed for $subjects[CN] ($cn_ip)!";
            syslog(LOG_ERR, "Authentication failed for $subjects[CN] ($cn_ip)!");
          }
        } else {
          $error = "The CN and client IP address doesnot match!";
          syslog(LOG_ERR, "Cannot sign the CSR b/c of the conflicts between IP Address of $subjects[CN] ($cn_ip) and $_SERVER[REMOTE_ADDR]");
        }
      } else {
        $error = "I cannot sign, CSR of this CN (hostname)!";
        syslog(LOG_ERR, "Cannot sign the CSR with CN=$subjects[CN] for $_SERVER[REMOTE_ADDR]");
      }
    } else {
      $error = "Unknown CSR format!";
      syslog(LOG_ERR, "Unknown CSR format from $_SERVER[REMOTE_ADDR]");
    }
  }
?>
<html>
  <head>
    <title>Signing CSR for nodes</title>
  </head>
  <body>
    <form method="post">
      <?php if (strlen($error) > 0) { ?>
      <div style="color: red;"><?php echo $error; ?></div>
      <?php } ?>
      CSR Content:<br/>
      <textarea rows="12" cols="80" name="csr"><?php if (isset($_POST["csr"]))
      echo $_POST["csr"]; ?></textarea>
      <br/>
      <input type="submit" value="Sign">
    <form>
  </body>
</html>
