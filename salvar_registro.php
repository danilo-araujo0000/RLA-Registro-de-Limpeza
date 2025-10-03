<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$conn = oci_connect('dbasistemas', 'dbasistemas', '172.19.0.250:1521/prdamevo', 'AL32UTF8');
if (!$conn) {
    die("Erro na conexão com o banco de dados Oracle");
}

$id_sala               = isset($_POST['id_sala']) ? $_POST['id_sala'] : null;
$colaborador           = isset($_POST['colaborador']) ? $_POST['colaborador'] : null;
$hora_limpeza          = isset($_POST['hora_limpeza']) ? $_POST['hora_limpeza'] : null;
$tipo_limpeza          = isset($_POST['tipo_limpeza']) ? $_POST['tipo_limpeza'] : null;
$obs                   = isset($_POST['obs']) ? $_POST['obs'] : null;
$portas                = isset($_POST['portas']) ? $_POST['portas'] : null;
$teto                  = isset($_POST['teto']) ? $_POST['teto'] : null;
$paredes               = isset($_POST['paredes']) ? $_POST['paredes'] : null;
$janelas               = isset($_POST['janelas']) ? $_POST['janelas'] : null;
$piso                  = isset($_POST['piso']) ? $_POST['piso'] : null;
$superficie_mobiliario = isset($_POST['superficie_mobiliario']) ? $_POST['superficie_mobiliario'] : null;
$dispenser             = isset($_POST['dispenser']) ? $_POST['dispenser'] : null;
$criticidade           = isset($_POST['criticidade']) ? $_POST['criticidade'] : null;

$sql = "INSERT INTO if_tbl_registro_higiene (
    ID_SALA, COLABORADOR, DATA_LIMPEZA, HORA_LIMPEZA, TIPO_LIMPEZA, OBS,
    PORTAS, TETO, PAREDES, JANELAS, PISO, SUPERFICIE_MOBILIARIO, DISPENSER, CRITICIDADE
) VALUES (
    :id_sala, :colaborador, SYSDATE, :hora_limpeza, :tipo_limpeza, :obs,
    :portas, :teto, :paredes, :janelas, :piso, :superficie_mobiliario, :dispenser, :criticidade
)";

$stid = oci_parse($conn, $sql);
oci_bind_by_name($stid, ':id_sala',               $id_sala);
oci_bind_by_name($stid, ':colaborador',           $colaborador);
oci_bind_by_name($stid, ':hora_limpeza',          $hora_limpeza);
oci_bind_by_name($stid, ':tipo_limpeza',          $tipo_limpeza);
oci_bind_by_name($stid, ':obs',                   $obs);
oci_bind_by_name($stid, ':portas',                $portas);
oci_bind_by_name($stid, ':teto',                  $teto);
oci_bind_by_name($stid, ':paredes',               $paredes);
oci_bind_by_name($stid, ':janelas',               $janelas);
oci_bind_by_name($stid, ':piso',                  $piso);
oci_bind_by_name($stid, ':superficie_mobiliario', $superficie_mobiliario);
oci_bind_by_name($stid, ':dispenser',             $dispenser);
oci_bind_by_name($stid, ':criticidade',           $criticidade);

$r = oci_execute($stid);
if ($r) {
    echo "<div style='text-align:center; margin-top:20px; font-family: sans-serif;'>
            <p style='font-size:18px;'>✅ Registro inserido com sucesso.</p>
            <button onclick='fecharAba()' 
                    style='padding:12px 24px; font-size:16px; background-color:#28a745; color:white; border:none; border-radius:5px;'>
                Fechar esta aba
            </button>
            <p id='msg' style='margin-top:15px; color:gray; font-size:14px;'></p>
          </div>

          <script>
          function fecharAba() {
              window.close();
              setTimeout(() => {
                  document.getElementById('msg').textContent = 
                      'Se a aba não foi fechada automaticamente, por favor feche manualmente.';
              }, 500);
          }
          </script>";
} else {
    $e = oci_error($stid);
    echo "Erro ao inserir registro: " . $e['message'];
}

oci_free_statement($stid);
oci_close($conn);
?>