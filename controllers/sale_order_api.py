from odoo import models, fields, api, http

class SaleOrderAPI(http.Controller):
    # Routes
    #Documenation
    @http.route('/api/v1/docs', auth='public', website=False)
    def docs(self):
        return http.request.render('api_odoo_rest.view_docs_template')

    @http.route('/api/v1/sale_order', type="json", auth="user",methods=["POST"],csrf=False)
    def create_sale_order(self, **kw):
        partner_id = http.request.env["res.partner"].sudo().search([("name", "=", kw["sale"]["partner_name"])])
        payment_term_id = http.request.env["account.payment.term"].sudo().search([("name", "=", kw["sale"]["payment_term"])])
        vals = {
            "partner_id": partner_id.id,
            "date_order": kw["sale"]["date_order"],
            "validity_date":  kw["sale"]["validity_date"],
            "payment_term_id": payment_term_id.id,
        }
        #Lista de precios
        if "listaPrecio" in kw["sale"]:
            vals["pricelist_id"] = http.request.env["product.pricelist"].sudo().search([("name", "=", kw["sale"]["listaPrecio"])]).id
        #SIM
        if "codSim" in kw["sale"]:
            vals["x_SIM"] = kw["sale"]["codSim"]
        #Almacen
        if "nombreAlmacen" in kw["sale"]:
            vals["warehouse_id"] = http.request.env["stock.warehouse"].sudo().search([("name", "=", kw["sale"]["nombreAlmacen"])]).id
        #Empleado
        if "nombreEmpleado" in kw["sale"]:
            vals["hr_employee_id"] = http.request.env["hr.employee"].sudo().search([("name", "=", kw["sale"]["nombreEmpleado"])]).id
        #Solicita
        if "solicita" in kw["sale"]:
            vals["hr_coach_id"] = http.request.env["hr.employee"].sudo().search([("name", "=", kw["sale"]["solicita"])]).id
        #Cliente
        if "hr_cliente" in kw["sale"]:
            vals["hr_partner_id"] = http.request.env["hr.employee"].sudo().search([("name", "=", kw["sale"]["hr_cliente"])]).id
        #Tipo de servicio
        if "tipoServicio" in kw["sale"]:
            vals["x_service_type"] = http.request.env["service.type"].sudo().search([("name", "=", kw["sale"]["tipoServicio"])]).id
        #Tipo de carga
        if "tipoCarga" in kw["sale"]:
            vals["x_carga_type"] = http.request.env["carga.type"].sudo().search([("name", "=", kw["sale"]["tipoCarga"])]).id
        #Etiquetas
        if "tag_names" in kw["sale"]:
            vals["tag_ids"] = http.request.env["crm.tag"].sudo().search([("name", "=", kw["sale"]["tag_names"])]).id
        #Unidad de negocio
        if "unidadNegocio" in kw["sale"]:
            vals["fleet_uNegocio"] = http.request.env["res.negocio"].sudo().search([("name", "=", kw["sale"]["unidadNegocio"])]).id
        #Numero de unidad
        if "numeroUnidad" in kw["sale"]:
            vals["fleet_uNegocio_id"] = http.request.env["fleet.vehicle"].sudo().search([("name", "=", kw["sale"]["numeroUnidad"])]).id
        sale = http.request.env["sale.order"].sudo().create(vals)
        ############################
        data = []
        for order_line in kw["order_line"]:
            producto_id = http.request.env["product.product"].sudo().search([("name", "=", order_line["product"])])
            line_data = {
                "order_id": sale.id,
                "product_id": producto_id.id,
                "product_uom_qty": order_line["product_uom_qty"],
            }
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
            "date_order": sale.date_order,
            "validity_date": sale.validity_date,
            "state": sale.state
        }, 200