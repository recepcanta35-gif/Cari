/* Only calls server-authorized state transitions; never computes stock/GL in JS. */
frappe.ui.form.on("Stock Assignment", {
  refresh(frm) {
    if (frm.doc.docstatus === 1) frm.add_custom_button("İade Oluştur", () => frappe.new_doc("Stock Assignment Return", {assignment: frm.doc.name}));
  }
});
frappe.ui.form.on("Daily Assignment", {
  refresh(frm) {
    if (frm.doc.docstatus !== 1) return;
    if (frm.doc.durum === "Planlandı") frm.add_custom_button("Göreve Başla", () => frm.call("start").then(()=>frm.reload_doc()));
    if (frm.doc.durum === "Sahada") frm.add_custom_button("Görevi Bitir", () => frappe.prompt({fieldname:"note",fieldtype:"Small Text",label:"Sonuç Notu",reqd:1}, ({note})=>frm.call("finish",{note}).then(()=>frm.reload_doc())));
  }
});
frappe.ui.form.on("Cari Shipment", {
  refresh(frm) {
    if (frm.doc.docstatus !== 1) return;
    if (frm.doc.status === "Hazırlanıyor") frm.add_custom_button("Sevk Et", () => frappe.prompt([{fieldname:"carrier",fieldtype:"Data",label:"Kargo Firması"},{fieldname:"tracking_number",fieldtype:"Data",label:"Takip Numarası"}], args=>frm.call("dispatch",args).then(()=>frm.reload_doc())));
    if (frm.doc.status === "Sevk Edildi") frm.add_custom_button("Teslimi Kaydet", () => frappe.prompt({fieldname:"note",fieldtype:"Small Text",label:"Teslim Notu",reqd:1},args=>frm.call("deliver",args).then(()=>frm.reload_doc())));
  }
});
frappe.ui.form.on("Cari Service Record", {
  refresh(frm) {
    if (frm.doc.docstatus !== 1) return;
    if (frm.doc.status === "Açık") frm.add_custom_button("Servise Başla",()=>frm.call("begin").then(()=>frm.reload_doc()));
    if (frm.doc.status === "İşlemde") frm.add_custom_button("Servisi Tamamla",()=>frappe.prompt({fieldname:"result",fieldtype:"Small Text",label:"Servis Sonucu",reqd:1},args=>frm.call("complete",args).then(()=>frm.reload_doc())));
  }
});
