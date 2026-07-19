from flask import Flask, render_template, request

app = Flask(__name__)

# Esta es nuestra "base de datos" de mentiras en memoria. 
# Si el servidor se reinicia, los cambios en el stock se borran, ojo.
inventario = {
    "1": {"nombre": "Running Max", "marca": "Nike", "talla": "41", "precio": 120000, "stock": 10},
    "2": {"nombre": "Classic Urban", "marca": "Adidas", "talla": "39", "precio": 95000, "stock": 15}
}

# Aquí guardamos las facturas que se vayan creando durante la sesión
historial_facturas = []

# La ruta principal acepta GET (para ver la página) y POST (cuando enviamos el formulario)
@app.route('/', methods=['GET', 'POST'])
def gestionar_tienda():
    mensaje = None
    tipo_alerta = "success"
    factura_actual = None

    # Si el usuario le dio clic a un botón del formulario...
    if request.method == 'POST':
        # Capturamos todos los datos que el usuario escribió en el HTML
        accion = request.form.get('accion')  # ¿Vender o Devolver?
        cliente = request.form.get('cliente')
        vendedor = request.form.get('vendedor')
        id_zapato = request.form.get('id_zapato')
        cantidad = int(request.form.get('cantidad', 1)) # Lo convertimos a entero para hacer matemáticas

        # Validamos que el zapato seleccionado realmente exista en nuestro inventario
        if id_zapato in inventario:
            zapato = inventario[id_zapato]
            total = zapato['precio'] * cantidad # Multiplicamos precio por cantidad
            
            # --- APRENDIENDO LÓGICA DE VENTA ---
            if accion == 'vender':
                if zapato['stock'] >= cantidad: # ¿Tenemos suficientes zapatos para vender?
                    zapato['stock'] -= cantidad  # Restamos las unidades del inventario
                    
                    # Creamos el recibo
                    factura_actual = {
                        "id": len(historial_facturas) + 1, # ID autoincremental rústico
                        "cliente": cliente,
                        "vendedor": vendedor,
                        "zapato": f"{zapato['marca']} {zapato['nombre']}",
                        "cantidad": cantidad,
                        "total": total,
                        "tipo": "VENTA"
                    }
                    historial_facturas.append(factura_actual) # Lo guardamos en el historial
                    mensaje = f"Venta procesada con éxito. Factura #{factura_actual['id']} generada."
                else:
                    # Si no hay stock, mandamos alerta roja de Bootstrap
                    mensaje = f"Error: No hay suficiente stock de {zapato['nombre']}. Disponibles: {zapato['stock']}"
                    tipo_alerta = "danger"
            
            # --- APRENDIENDO LÓGICA DE DEVOLUCIÓN ---
            elif accion == 'devolver':
                zapato['stock'] += cantidad  # Sumamos los zapatos que nos devolvieron al inventario
                
                # Creamos el recibo de devolución
                factura_actual = {
                    "id": len(historial_facturas) + 1,
                    "cliente": cliente,
                    "vendedor": vendedor,
                    "zapato": f"{zapato['marca']} {zapato['nombre']}",
                    "cantidad": cantidad,
                    "total": total,
                    "tipo": "DEVOLUCIÓN"
                }
                historial_facturas.append(factura_actual)
                mensaje = f"Devolución procesada. Se reincorporaron {cantidad} unidades al inventario."
                tipo_alerta = "warning" # Alerta amarilla para cambios o advertencias

    # Aquí ocurre la magia: enviamos los datos procesados en Python para que el HTML los dibuje
    return render_template('tienda.html', zapatos=inventario, mensaje=mensaje, tipo_alerta=tipo_alerta, factura=factura_actual)

if __name__ == '__main__':
    # El modo debug=True sirve para que el servidor se reinicie solo al guardar cambios
    app.run(debug=True)