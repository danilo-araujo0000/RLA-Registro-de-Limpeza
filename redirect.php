<?php
$id_sala = isset($_GET['sala']) ? intval($_GET['sala']) : 0;
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Redirecionando...</title>
</head>
<body onload="document.forms[0].submit();" style="text-align:center; font-family: sans-serif;">
    <p style="margin-top: 20px;">Redirecionando para o registro da sala <?php echo $id_sala; ?>...</p>
    <form action="registro.php" method="POST">
        <input type="hidden" name="id_sala" value="<?php echo $id_sala; ?>">
        <noscript>
            <p>JavaScript está desativado. Clique no botão para continuar.</p>
            <input type="submit" value="Continuar">
        </noscript>
    </form>
</body>
</html>
