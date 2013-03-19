<?php
  $error = "";
  if (isset($_POST["csr"])) {
    $csr = $_POST["csr"];
    $cn = null;
    $subjects = openssl_csr_get_subject($csr);
    if (isset($subjects["CN"])) {
      $cn = $subjects["CN"];
      if (preg_match('/\\.measurement-lab\\.org$/', $cn)) {
        $cn_ip = gethostbyname($cn);
        $client_ip = $_SERVER["REMOTE_ADDR"];
        if (strcmp($cn_ip, $client_ip) == 0) {
          $cacert = file_get_contents("/usr/share/openvpn/easy-rsa/2.0/keys/ca.crt");
          $privkey = file_get_contents("/usr/share/openvpn/easy-rsa/2.0/keys/ca.key");
          $usercert = openssl_csr_sign($csr, $cacert, $privkey, 3650);
          openssl_x509_export($usercert, $certout);
          header("Content-Type: application/octet-stream");
          header("Content-Disposition: attachment; filename=client.crt");
          echo $certout;
          return;
        } else {
          $error = "The CN and client IP address doesnot match!";
        }
      } else {
        $error = "I cannot sign, CSR of this CN (hostname)!";
      }
    } else {
      $error = "Unknown CSR format!";
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
