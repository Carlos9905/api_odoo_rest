from odoo import models, fields, api, http
from odoo.http import request, JsonRequest
class SaleOrderAPI(http.Controller):
    # Routes
    #Documenation
    @http.route('/api/v1/docs', auth='public', website=False)
    def docs(self):
        return http.request.render('sale_order_api_rest.view_docs_template')

    @http.route('/api/v1/sale_order', type="json", auth="user",methods=["POST"],csrf=False)
    def create_sale_order(self, **kw):
        #Datos de cabecera
        #if "partner_name" in kw["sale"] and "date_order" in kw["sale"] and "listaPrecio" in kw["sale"]:# and "nombreAlmacen" in kw["sale"]
        if "partner_name" in kw["sale"] and "listaPrecio" in kw["sale"] and "nombreAlmacen" in kw["sale"]:
            partner_id = http.request.env["res.partner"].sudo().search([("name", "=", kw["sale"]["partner_name"])])
            payment_term_id = http.request.env["account.payment.term"].sudo().search([("name", "=", kw["sale"]["payment_term"])])
            vals = {
                "partner_id": partner_id.id,
                #"date_order": kw["sale"]["date_order"],
                "validity_date":  kw["sale"]["validity_date"],
                "payment_term_id": payment_term_id.id,
            }
            #Lista de precios
            if "listaPrecio" in kw["sale"]:
                price_list = http.request.env["product.pricelist"].sudo().search([("name", "=", kw["sale"]["listaPrecio"])])
                if price_list:
                    vals["pricelist_id"] = price_list.id
                else:
                    return {"error": "Lista de precios no encontrada"}, 404
            #SIM
            if "codSim" in kw["sale"]:
                vals["x_SIM"] = kw["sale"]["codSim"]
            #Almacen
            if "nombreAlmacen" in kw["sale"]:
                warehose_id = http.request.env["stock.warehouse"].sudo().search([("name", "=", kw["sale"]["nombreAlmacen"])])
                if warehose_id:
                    vals["warehouse_id"] = warehose_id.id
                else:
                    return {"error": "Almacen no encontrado"}, 404
            #Empleado
            if "nombreEmpleado" in kw["sale"]:
                employee_id = http.request.env["hr.employee"].sudo().search([("name", "=", kw["sale"]["nombreEmpleado"])])
                if employee_id:
                    vals["employee_id"] = employee_id.id
                else:
                    return {"error": "Empleado no encontrado"}, 404
            #Solicita
            if "Solicita" in kw["sale"]:
                solicita_id = http.request.env["hr.employee"].sudo().search([("name", "=", kw["sale"]["Solicita"])])
                if solicita_id:
                    vals["hr_coach_id"] = solicita_id.id
                else:
                    return {"error": "Solicita no encontrado"}, 404
            """#Cliente
            if "hr_cliente" in kw["sale"]:
                cliente_id = http.request.env["res.partner"].sudo().search([("name", "=", kw["sale"]["hr_cliente"])])
                if cliente_id:
                    vals["cliente_id"] = cliente_id.id
                else:
                    return {"error": "Cliente no encontrado"}, 404"""
            #Autoriza
            if "Autoriza" in kw["sale"]:
                autoriza=http.request.env["hr.employee"].sudo().search([("name","=",kw["sale"]["Autoriza"])])
                if autoriza:
                    vals["hr_partner_id"]=autoriza.id
                else:
                    return {"error":"Empleado que autoriza no encontrado"},404
            #Tipo de servicio
            if "tipoServicio" in kw["sale"]:
                service_type = http.request.env["service.type"].sudo().search([("name", "=", kw["sale"]["tipoServicio"])])
                if service_type:
                    vals["x_service_type"] = service_type.id
                else:
                    return {"error": "Tipo de servicio no encontrado"}, 404
            #Tipo de carga
            if "tipoCarga" in kw["sale"]:
                tipoCarga = http.request.env["carga.type"].sudo().search([("name", "=", kw["sale"]["tipoCarga"])])
                if tipoCarga:
                    vals["x_carga_type"] = tipoCarga.id
                else:
                    return {"error": "Tipo de carga no encontrado"}, 404
            #Etiquetas
            if "tag_names" in kw["sale"]:
                tags_ids = []
                for tag_name in kw["sale"]["tag_names"]:
                    tag = http.request.env["crm.tag"].sudo().search([("name", "=", tag_name)])
                    if tag:
                        tags_ids.append(tag.id)
                    else:
                        return {"error": "Etiqueta no encontrada"}, 404
                vals["tag_ids"] = [(6, 0, tags_ids)]
            #Unidad de negocio
            if "unidadNegocio" in kw["sale"]:
                #unidadNegocio = http.request.env["fleet.uNegocio"].sudo().search([("name", "=", kw["sale"]["unidadNegocio"])])
                unidadNegocio = http.request.env["res.negocio"].sudo().search([("name", "=", kw["sale"]["unidadNegocio"])])
                if unidadNegocio:
                    vals["fleet_uNegocio"] = unidadNegocio.id
                else:
                    return {"error": "Unidad de negocio no encontrado"}, 404
            #Numero de unidad
            if "numeroUnidad" in kw["sale"]:
                #numeroUnidad = http.request.env["fleet.uNegocio_id"].sudo().search([("name", "=", kw["sale"]["numeroUnidad"])])
                numeroUnidad = http.request.env["fleet.vehicle"].sudo().search([("name", "=", kw["sale"]["numeroUnidad"])])
                if numeroUnidad:
                    vals["fleet_uNegocio_id"] = numeroUnidad.id
                else:
                    return {"error": "Numero de unidad no encontrado"}, 404
            
            sale = http.request.env["sale.order"].sudo().create(vals)
            # Lineas de productos
            data = []
            for order_line in kw["order_line"]:
                producto_id = http.request.env["product.product"].sudo().search([("name", "=", order_line["product"])])
                if producto_id:
                    line_data = {
                        "order_id": sale.id,
                        "product_id": producto_id.id,
                        "product_uom_qty": order_line["product_uom_qty"],
                    }
                else:
                    return {"error": "Producto no encontrado"}, 404
                #Precio unitario
                if "price_unit" in order_line:
                    line_data["price_unit"] = order_line["price_unit"]
                #Impuestos
                if "tax" in order_line:
                    tax_ids = []
                    for tax_name in order_line["tax"]:
                        tax = http.request.env["account.tax"].sudo().search([("name", "=", tax_name)])
                        if tax:
                            tax_ids.append(tax.id)
                    line_data["tax_id"] = [(6, 0, tax_ids)]
                data.append(line_data)
            http.request.env["sale.order.line"].sudo().create(data)
            return {
                "id": sale.id,
                "name": sale.name,
                #"date_order": sale.date_order,
                "validity_date": sale.validity_date,
                "state": sale.state
            }, 200
        else:
            return {
                "error": "Datos incompletos"
            }, 400