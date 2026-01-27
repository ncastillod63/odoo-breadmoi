# 🍞 Odoo Bread Moi – Docker Setup

Database name: bread_moi

Email: admin@breadmoi.com

Password: (definir por el equipo)

Language: Spanish (CO)

Country: Colombia

❌ Demo data: desmarcado

Haz clic en Create database.

🧩 Módulos usados (Odoo Community)

Ventas

Compras

Inventario

Manufactura

Facturación (se instala automáticamente)

⚠️ Nota:
Este proyecto usa Odoo Community, por lo tanto:

No incluye contabilidad avanzada

Los costos se manejan como costos estándar manuales

🧮 Costos y manufactura

Los costos de insumos se configuran en:

Producto → Información general → Costo

La receta del pan se gestiona con:

Lista de materiales (BoM)

El costo del pan se calcula a partir de:

Insumos + costos indirectos (fuera de Odoo)

👥 Trabajo en equipo (Git)
Flujo recomendado

main: rama estable

feature/nombre-cambio: una rama por cambio o mejora

Ejemplo:

git checkout -b feature/costos-pan
git add .
git commit -m "Ajuste de costos estándar del pan"
git push -u origin feature/costos-pan


Luego abrir Pull Request en GitHub.

🚫 Archivos que NO se suben al repo

Base de datos

Volúmenes Docker

Filestore de Odoo

Archivos con contraseñas reales

Estos ya están excluidos en el .gitignore.

🏷️ Proyecto académico / práctico

Este repositorio sirve como:

Caso práctico de implementación Odoo

Ejercicio de levantamiento de requerimientos

Simulación real de gestión operativa en panadería

📬 Contacto

Proyecto desarrollado para Bread Moi
Implementación y documentación: Equipo de proyecto
