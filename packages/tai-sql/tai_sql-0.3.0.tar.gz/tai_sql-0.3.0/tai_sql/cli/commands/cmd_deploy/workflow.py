import click
from pathlib import Path
from tai_sql import pm

def create_workflow_file() -> bool:
    """
    Crea el workflow de GitHub Actions para TAI-SQL deploy
    
    Args:
        project_root: Directorio raíz del proyecto
        
    Returns:
        True si se creó exitosamente
    """
    try:
        # Crear directorio .github/workflows si no existe

        workflows_dir = Path('.github') / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Contenido del workflow
        workflow_content = '''name: TAI-SQL Deploy

on:
  workflow_dispatch:
    inputs:
      entorno:
        description: 'Entorno de despliegue'
        required: true
        type: choice
        options:
          - development
          - preproduction
          - production
        default: 'development'
      schema:
        description: 'Nombre del esquema a desplegar'
        required: true
        type: string
        default: 'public'

env:
  PYTHON_VERSION: '3.11'

jobs:
  validate:
    name: 🔍 Validar cambios (${{ inputs.entorno }}/${{ inputs.schema }})
    runs-on: ubuntu-latest
    environment: ${{ inputs.entorno }}
    
    outputs:
      has-changes: ${{ steps.dry-run.outputs.has-changes }}
      changes-summary: ${{ steps.dry-run.outputs.changes-summary }}
      has-destructive: ${{ steps.dry-run.outputs.has-destructive }}
      
    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: 📦 Install TAI-SQL
        run: |
          python -m pip install --upgrade pip
          pip install tai-sql
      
      - name: 🔧 Configure TAI-SQL environment
        run: |
          echo "🔧 Configurando TAI-SQL para entorno: ${{ inputs.entorno }}"
          echo "📂 Schema: ${{ inputs.schema }}"
          
          # Verificar que tenemos la URL de base de datos
          if [ -z "${{ secrets.''' + pm.db.provider.var_name + '''}}" ]; then
            echo "❌ ''' + pm.db.provider.var_name + ''' no está configurada para el entorno ${{ inputs.entorno }}"
            exit 1
          fi
          
          echo "✅ Base de datos configurada"
      
      - name: 🔍 Dry run - Validar cambios
        id: dry-run
        env:
          ''' + pm.db.provider.var_name + ''': ${{ secrets.''' + pm.db.provider.var_name + ''' }}
        run: |
          echo "🚀 Ejecutando validación de esquema..."
          echo "::group::TAI-SQL Push Dry Run"
          
          # Ejecutar tai-sql push en modo dry-run y capturar salida
          OUTPUT_FILE="/tmp/tai-sql-output.log"
          EXIT_CODE=0
          
          # Ejecutar el comando y capturar tanto stdout como stderr
          tai-sql push --schema "${{ inputs.schema }}" --dry-run --verbose 2>&1 | tee "$OUTPUT_FILE" || EXIT_CODE=$?
          
          echo "::endgroup::"
          
          # Procesar la salida para extraer información
          if [ $EXIT_CODE -eq 0 ]; then
            echo "✅ Validación completada exitosamente"
            
            # Verificar si hay cambios detectados
            if grep -q "No se detectaron cambios\\|Sin cambios detectados" "$OUTPUT_FILE"; then
              echo "has-changes=false" >> $GITHUB_OUTPUT
              echo "changes-summary=Sin cambios detectados en el esquema" >> $GITHUB_OUTPUT
              echo "has-destructive=false" >> $GITHUB_OUTPUT
              echo "ℹ️ No se detectaron cambios en el esquema"
            else
              echo "has-changes=true" >> $GITHUB_OUTPUT
              
              # Verificar si hay cambios destructivos
              if grep -q "⚠️\\|DESTRUCTIVO\\|DROP\\|ALTER.*DROP" "$OUTPUT_FILE"; then
                echo "has-destructive=true" >> $GITHUB_OUTPUT
                echo "🚨 Cambios destructivos detectados - requiere aprobación manual"
              else
                echo "has-destructive=false" >> $GITHUB_OUTPUT
                echo "✅ Cambios seguros detectados"
              fi
              
              # Extraer resumen de cambios (capturar más contexto)
              CHANGES_SUMMARY=$(cat "$OUTPUT_FILE" | grep -A 30 -B 5 "📋\\|Cambios detectados\\|Sentencias DDL\\|🔧\\|CREATE\\|DROP\\|ALTER" | head -50 || echo "Cambios detectados - ver logs para detalles")
              echo "changes-summary<<EOF" >> $GITHUB_OUTPUT
              echo "$CHANGES_SUMMARY" >> $GITHUB_OUTPUT
              echo "EOF" >> $GITHUB_OUTPUT
            fi
          else
            echo "❌ Error durante la validación (Exit code: $EXIT_CODE)"
            cat "$OUTPUT_FILE"
            exit $EXIT_CODE
          fi
      
      - name: 📊 Crear reporte de validación
        if: steps.dry-run.outputs.has-changes == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{ inputs.entorno }}';
            const schema = '${{ inputs.schema }}';
            const changesSummary = `${{ steps.dry-run.outputs.changes-summary }}`;
            const hasDestructive = '${{ steps.dry-run.outputs.has-destructive }}' === 'true';
            const runUrl = `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`;
            
            const destructiveWarning = hasDestructive ? 
              `### 🚨 **ATENCIÓN: Cambios Destructivos Detectados**
              
              Este deployment contiene operaciones que pueden causar pérdida de datos.
              **Revisa cuidadosamente los cambios antes de aprobar.**
              
              ` : '';
            
            const body = `## 🔍 Validación TAI-SQL - Esperando Aprobación
            
            **Entorno:** \\`${entorno}\\`  
            **Schema:** \\`${schema}\\`  
            **Status:** ⏳ Pendiente de aprobación  
            **Tipo:** ${hasDestructive ? '🚨 Cambios Destructivos' : '✅ Cambios Seguros'}
            
            ${destructiveWarning}### 📋 Cambios Detectados:
            <details>
            <summary>Ver detalles de los cambios</summary>
            
            \\`\\`\\`
            ${changesSummary}
            \\`\\`\\`
            </details>
            
            ### ⚠️ Acción Requerida
            ${hasDestructive ? 
              'Este deployment contiene **cambios destructivos** que requieren revisión manual cuidadosa.' :
              'Este deployment contiene cambios seguros pero requiere aprobación.'
            }
            
            **Para aprobar:** Un reviewer debe aprobar el environment \\`${entorno}\\` en la pestaña Environments.
            
            **Para cancelar:** Cancela este workflow run.
            
            ### 🔗 Enlaces útiles
            - [Ver logs completos](${runUrl})
            - [Environments](/${{ github.repository }}/settings/environments)
            
            ---
            *Workflow iniciado por @${{ github.actor }}*`;
            
            // Crear issue comment si es un PR, sino crear un issue
            if (context.payload.pull_request) {
              await github.rest.issues.createComment({
                issue_number: context.payload.pull_request.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            } else {
              // Crear issue para tracking
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `🔍 TAI-SQL Validation - ${entorno}/${schema} - ${hasDestructive ? 'DESTRUCTIVE' : 'SAFE'}`,
                body: body,
                labels: ['tai-sql', 'deployment', 'validation', hasDestructive ? 'destructive' : 'safe']
              });
            }

  deploy:
    name: 🚀 Deploy cambios (${{ inputs.entorno }}/${{ inputs.schema }})
    runs-on: ubuntu-latest
    needs: validate
    environment: ${{ inputs.entorno }}
    if: needs.validate.outputs.has-changes == 'true'
    
    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: 📦 Install TAI-SQL
        run: |
          python -m pip install --upgrade pip
          pip install tai-sql
      
      - name: 🔧 Configure TAI-SQL environment
        run: |
          echo "🔧 Configurando TAI-SQL para deployment en: ${{ inputs.entorno }}"
          echo "📂 Schema: ${{ inputs.schema }}"
          
          # Mostrar información de cambios detectados
          echo "📊 Cambios detectados: ${{ needs.validate.outputs.has-changes }}"
          echo "🚨 Cambios destructivos: ${{ needs.validate.outputs.has-destructive }}"
      
      - name: 🚀 Deploy schema changes
        env:
          ''' + pm.db.provider.var_name + ''': ${{ secrets.''' + pm.db.provider.var_name + ''' }}
        run: |
          echo "🚀 Ejecutando deployment de esquema..."
          echo "::group::TAI-SQL Push Deploy"
          
          # Ejecutar tai-sql push en modo force con logging detallado
          tai-sql push --schema "${{ inputs.schema }}" --force --verbose
          
          echo "::endgroup::"
          echo "✅ Deployment completado exitosamente"
      
      - name: 📊 Reporte de deployment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{ inputs.entorno }}';
            const schema = '${{ inputs.schema }}';
            const status = '${{ job.status }}';
            const hasDestructive = '${{ needs.validate.outputs.has-destructive }}' === 'true';
            const runUrl = `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`;
            
            let statusEmoji = '';
            let statusText = '';
            
            switch(status) {
              case 'success':
                statusEmoji = '✅';
                statusText = 'Completado exitosamente';
                break;
              case 'failure':
                statusEmoji = '❌';
                statusText = 'Falló durante la ejecución';
                break;
              case 'cancelled':
                statusEmoji = '🚫';
                statusText = 'Cancelado';
                break;
              default:
                statusEmoji = '⚠️';
                statusText = 'Estado desconocido';
            }
            
            const body = `## ${statusEmoji} TAI-SQL Deployment - ${statusText}
            
            **Entorno:** \\`${entorno}\\`  
            **Schema:** \\`${schema}\\`  
            **Status:** ${statusText}  
            **Tipo:** ${hasDestructive ? '🚨 Cambios Destructivos' : '✅ Cambios Seguros'}  
            **Ejecutado por:** @${{ github.actor }}
            
            ### 📊 Detalles del Deployment:
            - **Workflow Run:** [Ver detalles](${runUrl})
            - **Commit:** \\`${{ github.sha }}\\`
            - **Branch:** \\`${{ github.ref_name }}\\`
            - **Timestamp:** ${new Date().toISOString()}
            
            ### ${status === 'success' ? '🎉 Resultado' : '⚠️ Error'}
            ${status === 'success' ? 
              `El schema \\`${schema}\\` ha sido actualizado exitosamente en la base de datos del entorno \\`${entorno}\\`.` : 
              'Revisa los logs del workflow para más detalles sobre el error.'}
            
            ${hasDestructive && status === 'success' ? '⚠️ **Nota:** Este deployment incluyó cambios destructivos que fueron revisados y aprobados.' : ''}
            
            ### 📋 Próximos pasos
            ${status === 'success' ? 
              `- Verificar que la aplicación funciona correctamente
              - Ejecutar tests de integración si están disponibles
              - Monitorear la aplicación en busca de errores` :
              `- Investigar y corregir el error
              - Re-ejecutar el workflow una vez solucionado
              - Considerar rollback si es necesario`}
            `;
            
            // Crear issue comment si es un PR, sino crear un issue
            if (context.payload.pull_request) {
              await github.rest.issues.createComment({
                issue_number: context.payload.pull_request.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            } else {
              // Crear issue para tracking del resultado
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `${statusEmoji} TAI-SQL Deploy - ${entorno}/${schema} - ${statusText}`,
                body: body,
                labels: ['tai-sql', 'deployment', status === 'success' ? 'success' : 'failed', hasDestructive ? 'destructive' : 'safe']
              });
            }

  no-changes:
    name: ℹ️ Sin cambios detectados
    runs-on: ubuntu-latest
    needs: validate
    if: needs.validate.outputs.has-changes == 'false'
    
    steps:
      - name: 📊 Reporte sin cambios
        uses: actions/github-script@v7
        with:
          script: |
            const entorno = '${{ inputs.entorno }}';
            const schema = '${{ inputs.schema }}';
            const runUrl = `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`;
            
            const body = `## ℹ️ TAI-SQL Validation - Sin Cambios
            
            **Entorno:** \\`${entorno}\\`  
            **Schema:** \\`${schema}\\`  
            **Status:** ✅ Schema sincronizado
            
            ### 📊 Resultado
            El esquema \\`${schema}\\` está completamente sincronizado con la base de datos del entorno \\`${entorno}\\`.
            
            No se detectaron diferencias entre el código y la base de datos actual.
            
            ### 📋 Detalles
            - **Workflow Run:** [Ver detalles](${runUrl})
            - **Commit:** \\`${{ github.sha }}\\`
            - **Branch:** \\`${{ github.ref_name }}\\`
            - **Timestamp:** ${new Date().toISOString()}
            
            ---
            *Validación ejecutada por @${{ github.actor }}*`;
            
            // Solo crear comment en PR
            if (context.payload.pull_request) {
              await github.rest.issues.createComment({
                issue_number: context.payload.pull_request.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            }
'''
        
        # Escribir el archivo
        workflow_file = workflows_dir / 'database.yml'
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        return True
        
    except Exception as e:
        click.echo(f"❌ Error al crear workflow: {e}")
        return False
