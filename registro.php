<?php
	$conn = oci_connect('dbasistemas', 'dbasistemas', '172.19.0.250:1521/prdamevo', 'AL32UTF8');
	if (!$conn) {
		die("Erro na conexão com o banco de dados Oracle");
	}
	$id_sala = isset($_POST['id_sala']) ? intval($_POST['id_sala']) : 1;
	
	$query = oci_parse($conn, "
    SELECT s.nome_sala, st.nome_setor
    FROM if_tbl_sala_higiene s
    JOIN if_tbl_setores_higiene st ON s.id_setor = st.id_setor
    WHERE s.id_sala = :id_sala
	");
	oci_bind_by_name($query, ":id_sala", $id_sala);
	oci_execute($query);
	$sala = oci_fetch_assoc($query);
	
	if (!$sala) {
		die("Sala não encontrada!");
	}
?>

<!DOCTYPE html>
<html lang="pt">
	<head>
		<meta charset="UTF-8">
		<title>Registro de Limpeza</title>
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
		<style>
			body { background-color: #565657ff; }
			.card { width: 80%; margin: auto; padding: 35px; border-radius: 0px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }
			.btn-success { width: 100%; }
			#camposTerminal { display: none; }
		</style>
	</head>
	<body>
		<div class="card">
			<h2 class="text-center">Registro de Limpeza</h2>
			
			<div class="mb-3">
				<label class="form-label">Setor:</label>
				<input type="text" class="form-control" value="<?php echo htmlspecialchars($sala['NOME_SETOR']); ?>" disabled>
			</div>
			
			<div class="mb-3">
				<label class="form-label">Sala:</label>
				<input type="text" class="form-control" value="<?php echo htmlspecialchars($sala['NOME_SALA']); ?>" disabled>
			</div>
			
			<form action="salvar_registro.php" method="POST">
				<input type="hidden" name="id_sala" value="<?php echo $id_sala; ?>">
				
				<div class="mb-3">
					<label class="form-label">Colaborador:</label>
					<input type="text" name="colaborador" class="form-control" required>
				</div>
				
				<div class="row">
					<div class="col-md-6 mb-3">
						<label class="form-label">Data:</label>
						<input type="date" name="data" id="data" class="form-control" required>
					</div>
					<div class="col-md-6 mb-3">
						<label class="form-label">Hora da Limpeza:</label>
						<input type="time" name="hora_limpeza" id="hora_limpeza" class="form-control" required>
					</div>
				</div>
				
				<div class="mb-3">
					<label class="form-label">Tipo de Limpeza:</label>
					<select name="tipo_limpeza" id="tipo_limpeza" class="form-select" required>
						<option value="concorrente">Concorrente</option>
						<option value="terminal">Terminal</option>
					</select>
				</div>
				
				<!-- Campos adicionais para Terminal -->
				<div id="camposTerminal">
					<div class="mb-3">
						<label class="form-label">Criticidade:</label>
						<select name="criticidade" id="criticidade" class="form-select">
							<option value="">-- Selecione --</option>
							<option value="critico">Crítico</option>
							<option value="semi-critico">Semi-crítico</option>
							<option value="nao critico">Não crítico</option>
						</select>
					</div>
					
					<div class="row">
						<div class="col-md-6 mb-3">
							<label class="form-label">Portas:</label>
							<select name="portas" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
						<div class="col-md-6 mb-3">
							<label class="form-label">Teto:</label>
							<select name="teto" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
					</div>
					
					<div class="row">
						<div class="col-md-6 mb-3">
							<label class="form-label">Paredes:</label>
							<select name="paredes" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
						<div class="col-md-6 mb-3">
							<label class="form-label">Janelas:</label>
							<select name="janelas" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
					</div>
					
					<div class="row">
						<div class="col-md-6 mb-3">
							<label class="form-label">Piso:</label>
							<select name="piso" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
						<div class="col-md-6 mb-3">
							<label class="form-label">Superfície/Mobiliário:</label>
							<select name="superficie_mobiliario" class="form-select">
								<option value="">-- Selecione --</option>
								<option value="S">S</option>
								<option value="N">N</option>
								<option value="NA">NA</option>
							</select>
						</div>
					</div>
					
					<div class="col-md-6 mb-3">
						<label class="form-label">Dispenser:</label>
						<select name="dispenser" class="form-select">
							<option value="">-- Selecione --</option>
							<option value="S">S</option>
							<option value="N">N</option>
							<option value="NA">NA</option>
						</select>
					</div>
				</div>
				
				<button type="submit" class="btn btn-success">Registrar</button>
			</form>
		</div>
		
		<script>
			function preencherDataHora() {
				const agora = new Date();
				
				// Preenche o campo de data com o formato YYYY-MM-DD
				document.getElementById("data").value = agora.toISOString().split('T')[0];
				
				// Preenche o campo de hora com o formato HH:MM
				const horas = String(agora.getHours()).padStart(2, '0');
				const minutos = String(agora.getMinutes()).padStart(2, '0');
				document.getElementById("hora_limpeza").value = `${horas}:${minutos}`;
			}
			
			function toggleCamposTerminal() {
				const tipoLimpeza = document.getElementById("tipo_limpeza").value;
				const camposTerminal = document.getElementById("camposTerminal");
				
				const camposObrigatorios = ["criticidade"];
				
				if (tipoLimpeza === "terminal") {
					camposTerminal.style.display = "block";
					camposObrigatorios.forEach(campo => {
						document.getElementById(campo).setAttribute("required", "required");
					});
					} else {
					camposTerminal.style.display = "none";
					camposObrigatorios.forEach(campo => {
						document.getElementById(campo).removeAttribute("required");
					});
				}
			}
			
			window.onload = () => {
				preencherDataHora(); // Preenche automaticamente os campos de data e hora
				document.getElementById("tipo_limpeza").addEventListener("change", toggleCamposTerminal);
				toggleCamposTerminal(); // Garante que os campos sejam mostrados ou escondidos corretamente
			};
		</script>
	</body>
</html>
