frappe.pages["cari-merkez"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({parent: wrapper, title: "Cari İş Merkezi", single_column: true});
  const root = document.createElement("div");
  root.className = "cari-center";
  root.innerHTML = `<style>
    .cari-center{padding:20px;max-width:1200px;margin:auto}.cari-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:22px 0}.cari-card{background:var(--card-bg,#fff);border:1px solid var(--border-color,#ddd);border-radius:12px;padding:20px}.cari-card strong{display:block;font-size:26px;margin-top:12px}.cari-links{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:24px}.cari-table{overflow:auto}.cari-table table{width:100%}.cari-table td,.cari-table th{padding:10px;border-bottom:1px solid var(--border-color,#ddd);white-space:nowrap}.cari-note{color:var(--text-muted);font-size:12px}
    </style><p class="cari-subtitle"></p><div class="cari-cards"></div><div class="cari-links"></div><div class="cari-table"></div><p class="cari-note">Gösterilen veriler kullanıcı kapsamıyla sınırlıdır. Üretim kabulü ve canlı entegrasyon ayrı teslim kapılarıdır.</p>`;
  page.main[0].append(root);
  const currency = (n, c) => new Intl.NumberFormat("tr-TR", {style: "currency", currency: c || "TRY"}).format(n);
  const card = (label, value) => {
    const element = document.createElement("div"); element.className = "cari-card";
    const text = document.createElement("span"); text.textContent = label;
    const number = document.createElement("strong"); number.textContent = value;
    element.append(text, number); root.querySelector(".cari-cards").append(element);
  };
  const links = [["Stock Assignment","Zimmetler"],["Stock Assignment Return","Zimmet İadeleri"],["Daily Assignment","Günlük Görevler"],["Sales Order","Siparişler"],["Cari Shipment","Sevkiyat"],["Cari Payment Instrument","Çek / Senet"],["Cari Service Record","Servis"]];
  for (const [doctype, label] of links) {
    if (!frappe.boot.user.can_read.includes(doctype)) continue;
    const button = document.createElement("button"); button.className = "btn btn-default"; button.textContent = label;
    button.onclick = () => frappe.set_route("List", doctype);
    root.querySelector(".cari-links").append(button);
  }
  frappe.call({method: "cari_custom.api.dashboard"}).then(({message: data}) => {
    root.querySelector(".cari-subtitle").textContent = `${data.company} · ${data.persona}`;
    if (data.open_tasks !== undefined) card("Açık görev", data.open_tasks);
    if (data.stock_rows !== undefined) card("Depo / ürün satırı", data.stock_rows);
    if (data.sales_base_total !== undefined) card("Net fatura toplamı", currency(data.sales_base_total, data.currency));
    if (data.customer_balance_base !== undefined) card("Cari bakiye", currency(data.customer_balance_base, data.currency));
  });
  const printRows = (rows) => {
    const table = document.createElement("table"); table.className = "table";
    const header = table.createTHead().insertRow();
    for (const title of ["Kod", "Ürün", "Birim", "Depo", "Miktar", "Rezerve"]) { const cell = document.createElement("th"); cell.textContent = title; header.append(cell); }
    const body = table.createTBody();
    for (const row of rows) {
      const tr = body.insertRow();
      for (const val of [row.item_code,row.item_name,row.stock_uom,row.warehouse,row.actual_qty,row.reserved_qty]) tr.insertCell().textContent = val;
    }
    root.querySelector(".cari-table").replaceChildren(table);
  };
  if (frappe.boot.user.can_read.includes("Warehouse")) {
    frappe.call({method: "cari_custom.api.quantity_stock"}).then(({message}) => printRows(message));
    page.add_inner_button("Miktar CSV", () => { window.location.assign("/api/method/cari_custom.api.export_quantity_stock"); });
  }
  if (frappe.user.has_role("System Manager") || frappe.user.has_role("Cari Kullanıcı Yöneticisi") || frappe.user.has_role("Cari Yönetici")) {
    page.add_inner_button("Kullanıcı Oluştur", () => {
      const dialog = new frappe.ui.Dialog({title:"Kapsamlı Kullanıcı Oluştur",fields:[
        {fieldname:"email",fieldtype:"Data",label:"E-posta",reqd:1,options:"Email"},
        {fieldname:"first_name",fieldtype:"Data",label:"Ad",reqd:1},
        {fieldname:"company",fieldtype:"Link",options:"Company",label:"Şirket",reqd:1},
        {fieldname:"persona",fieldtype:"Select",options:"Satış\nSaha\nDepo\nServis\nPortal",label:"Profil",reqd:1},
        {fieldname:"employee",fieldtype:"Link",options:"Employee",label:"Saha Personeli"},
        {fieldname:"customers",fieldtype:"Small Text",label:"Müşteri kimlikleri (satır başına bir)"},
        {fieldname:"warehouses",fieldtype:"Small Text",label:"Depo kimlikleri (satır başına bir)"},
        {fieldname:"reason",fieldtype:"Small Text",label:"Gerekçe",reqd:1}],
        primary_action_label:"Güvenli Hesap Oluştur",primary_action(values){
          for(const key of ["customers","warehouses"]) values[key] = JSON.stringify((values[key] || "").split("\n").map(s=>s.trim()).filter(Boolean));
          frappe.call({method:"cari_custom.user_management.provision_user",args:values}).then(()=>{dialog.hide();frappe.msgprint("Hesap ve kapsam oluşturuldu. Yeni hesap SMTP davetine kadar pasiftir; parola gösterilmez.");});
        }}); dialog.show();
    });
  }
};
