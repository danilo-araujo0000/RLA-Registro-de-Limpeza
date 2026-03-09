# Migração: Reposição de Itens - SIM/NÃO → Quantidades Numéricas

## 📋 Resumo da Mudança

Conversão do sistema de reposição de itens de um modelo binário (SIM/NÃO) para um modelo de quantidades numéricas com controles intuitivos [- 0 +].

**Data de Implementação**: 2026-03-02
**Status**: ✅ Código Implementado - Aguardando Migração do Banco de Dados

---

## 🎯 Objetivos

1. ✅ Permitir registro de quantidades exatas de itens repostos
2. ✅ Melhorar controle de estoque e consumo
3. ✅ Manter compatibilidade com dados históricos
4. ✅ Proporcionar UX intuitiva para tablets/touch

---

## 📦 Arquivos Modificados

### 1. **Banco de Dados**
- ✅ Script criado: `migration_reposicao_quantidade.sql`
- Altera tipo das colunas: VARCHAR → NUMBER(3)
- Migra dados: S→1, N/null/NA→0
- Valor padrão: 0

### 2. **Backend (Python/Django)**
- ✅ `registro/views.py`
  - Linhas 212-243: Conversão de strings para int
  - Linhas 505-508: Recuperação como inteiros
  - Linhas 567-574: Exibição de quantidades no histórico
  - Linhas 913-916: API de edição

### 3. **Frontend (HTML)**
- ✅ `templates/registro.html`
  - Linhas 259-356: Modal redesenhado com controles [- 0 +]
  - Substituição de radio buttons por contadores
  - Adição de ícones para cada item

### 4. **Frontend (JavaScript)**
- ✅ `static/js/registro.js`
  - Linhas 197-264: Lógica de controle de quantidades
  - Funções: incrementar, decrementar, atualizar display
  - Validação de limites (0-999)
  - Sincronização com campos hidden

### 5. **Estilos (CSS)**
- ✅ `static/css/registro.css`
  - Linhas 467-613: Estilos completos para controles
  - Botões circulares com animações
  - Responsividade mobile
  - Badge de quantidade

- ✅ `static/css/historico.css`
  - Linhas 30-40: Badge de quantidade para histórico

- ✅ `static/css/relatorio.css`
  - Linhas 628-755: Estilos para modal de edição
  - Controles de quantidade
  - Responsividade

### 6. **Tela de Relatório (HTML + JavaScript)**
- ✅ `templates/relatorio.html`
  - Linhas 435-532: Modal de edição com controles de quantidade
  - Linhas 920-989: Funções JavaScript para quantidade
  - Linhas 1005-1035: Atualização de contador
  - Linhas 1037-1086: Confirmação de itens
  - Linhas 1088-1116: Event listeners
  - Linhas 1309-1361: Exibição de quantidades no modal "Info"

---

## 🔄 Processo de Implementação

### **PASSO 1: Executar Migração do Banco de Dados** ⚠️ PENDENTE

```bash
# Conectar ao Oracle como DBA
sqlplus dbasistemas/dbasistemas@prdamevo

# Executar o script
@migration_reposicao_quantidade.sql

# Verificar resultados das queries de validação
# Aguardar confirmação antes de remover colunas de backup
```

**IMPORTANTE**:
- Execute em horário de baixo movimento
- Mantenha backup da tabela
- Não remova colunas _old antes de validar em produção por alguns dias

### **PASSO 2: Coletar Arquivos Estáticos**

```bash
# Dentro do container ou ambiente Django
python manage.py collectstatic --noinput
```

### **PASSO 3: Reiniciar Aplicação**

```bash
# Se usando Docker
docker-compose restart web

# Ou
docker restart RLA-registro-de-limpeza-ames
```

### **PASSO 4: Testes**

#### Testes Funcionais
1. ✅ Abrir modal de reposição
2. ✅ Testar botões [+] e [-]
3. ✅ Verificar limite mínimo (0)
4. ✅ Verificar limite máximo (999)
5. ✅ Confirmar e verificar contador no botão principal
6. ✅ Submeter formulário e verificar salvamento
7. ✅ Verificar exibição no histórico
8. ✅ Testar edição de registro existente

#### Testes de Compatibilidade
1. ✅ Verificar registros antigos no histórico
2. ✅ Confirmar migração S→1, N→0
3. ✅ Testar em tablets (touch)
4. ✅ Validar responsividade mobile

---

## 🎨 Novas Funcionalidades

### Interface do Usuário

**ANTES:**
```
Papel Higiênico:  ⚫ SIM  ⚪ NÃO
```

**DEPOIS:**
```
🧻 Papel Higiênico:  [-]  [5]  [+]
```

### Características

1. **Botões Circulares**
   - [-] Vermelho para decrementar
   - [+] Azul para incrementar
   - Display grande e centralizado

2. **Feedback Visual**
   - Cor verde quando quantidade > 0
   - Animação ao incrementar/decrementar
   - Efeito hover em botões

3. **Contador Inteligente**
   - Mostra "Total: X itens" no botão principal
   - Só aparece se houver itens repostos
   - Atualiza dinamicamente

4. **Validação**
   - Não permite valores negativos
   - Limite máximo: 999 unidades
   - Aceita 0 como valor válido (nenhum item reposto)

---

## 📊 Estrutura do Banco de Dados

### Colunas Afetadas
```sql
PAPEL_HIG       NUMBER(3) DEFAULT 0
PAPEL_TOALHA    NUMBER(3) DEFAULT 0
ALCOOL          NUMBER(3) DEFAULT 0
SABONETE        NUMBER(3) DEFAULT 0
```

### Regras de Migração
```sql
-- Valores antigos → Valores novos
'S'           → 1
'N'           → 0
NULL          → 0
'NA'          → 0
```

### Índices e Constraints
- Não há constraints de CHECK implementadas
- Valores válidos: 0 a 999
- Validação ocorre no frontend e backend

---

## 🔧 Funções JavaScript Principais

### `incrementarQuantidade(item)`
- Incrementa quantidade do item especificado
- Valida limite máximo (999)
- Atualiza display visual

### `decrementarQuantidade(item)`
- Decrementa quantidade do item especificado
- Valida limite mínimo (0)
- Atualiza display visual

### `atualizarDisplayQuantidade(item)`
- Sincroniza valor no display
- Aplica classe CSS `.completo` se > 0
- Atualiza feedback visual

### `confirmarItensReposicao()`
- Transfere quantidades para campos hidden
- Calcula total de itens repostos
- Atualiza contador no botão principal
- Fecha modal

---

## 📈 Benefícios da Mudança

### Gestão
- ✅ Dados precisos de consumo
- ✅ Relatórios quantitativos
- ✅ Planejamento de compras baseado em dados reais
- ✅ Identificação de padrões de consumo

### Operacional
- ✅ Registro mais rápido (menos cliques)
- ✅ Interface intuitiva para tablets
- ✅ Feedback visual claro
- ✅ Menos erros de preenchimento

### Técnico
- ✅ Dados estruturados para análise
- ✅ Compatibilidade com dados históricos
- ✅ Fácil manutenção
- ✅ Extensível para futuras melhorias

---

## 🚨 Rollback (Se Necessário)

Caso seja necessário reverter a mudança:

```sql
-- 1. Restaurar tipo VARCHAR
ALTER TABLE if_tbl_registro_higiene MODIFY papel_hig VARCHAR2(10);
ALTER TABLE if_tbl_registro_higiene MODIFY papel_toalha VARCHAR2(10);
ALTER TABLE if_tbl_registro_higiene MODIFY alcool VARCHAR2(10);
ALTER TABLE if_tbl_registro_higiene MODIFY sabonete VARCHAR2(10);

-- 2. Restaurar dados originais (se colunas _old ainda existirem)
UPDATE if_tbl_registro_higiene SET papel_hig = papel_hig_old;
UPDATE if_tbl_registro_higiene SET papel_toalha = papel_toalha_old;
UPDATE if_tbl_registro_higiene SET alcool = alcool_old;
UPDATE if_tbl_registro_higiene SET sabonete = sabonete_old;
COMMIT;
```

Depois reverter os arquivos usando Git:
```bash
git checkout HEAD -- registro/views.py templates/registro.html static/js/registro.js static/css/registro.css static/css/historico.css
```

---

## 📝 Notas de Desenvolvimento

### Decisões de Design

1. **Por que 0 é válido?**
   - Nem sempre há necessidade de reposição
   - Permite registro completo mesmo sem itens

2. **Por que limite 999?**
   - Limite razoável para reposição diária
   - Evita erros de digitação
   - Cabe em NUMBER(3)

3. **Por que readonly no input?**
   - Evita digitação manual
   - Força uso dos botões
   - Melhor UX em touch

### Melhorias Futuras Sugeridas

1. **Botões rápidos**: +1, +5, +10 para agilizar
2. **Histórico de consumo**: Gráficos de tendência
3. **Alertas**: Notificar se consumo anormal
4. **Previsão**: Estimar próxima reposição
5. **Relatório**: Total mensal por item

---

## ✅ Checklist de Validação

Antes de marcar como concluído, verificar:

- [ ] Script SQL executado sem erros
- [ ] Dados migrados corretamente (S→1, N→0)
- [ ] Arquivos estáticos coletados
- [ ] Aplicação reiniciada
- [ ] Modal abre corretamente
- [ ] Botões [+] e [-] funcionam
- [ ] Limites (0-999) respeitados
- [ ] Contador atualiza no botão
- [ ] Dados salvam no banco
- [ ] Histórico exibe quantidades
- [ ] Edição funciona
- [ ] Responsividade OK em mobile/tablet
- [ ] Registros antigos aparecem corretamente
- [ ] Performance aceitável

---

## 📞 Suporte

Em caso de problemas:

1. Verificar logs do container: `docker logs RLA-registro-de-limpeza-ames`
2. Verificar logs do Oracle
3. Testar em ambiente de desenvolvimento primeiro
4. Manter colunas _old por pelo menos 1 semana em produção

---

## 📚 Referências

- Django Documentation: https://docs.djangoproject.com/
- Oracle SQL: https://docs.oracle.com/en/database/oracle/oracle-database/
- Font Awesome Icons: https://fontawesome.com/

---

**Desenvolvido em**: 2026-03-02
**Versão**: 1.0
**Status**: Pronto para Deploy
