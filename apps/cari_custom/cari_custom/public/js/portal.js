frappe.ready(() => {
  const cart = new Map();
  let requestId = null;
  const status = text => { document.getElementById("cari-status").textContent = text; };
  const money = (value, currency) => new Intl.NumberFormat("tr-TR", {style:"currency",currency}).format(value);
  const renderCart = () => {
    const root = document.getElementById("cari-cart-items"); root.replaceChildren();
    for (const [code, entry] of cart) {
      const row = document.createElement("p"); const name = document.createElement("span"); name.textContent = `${entry.name} (${code}) · `;
      const qty = document.createElement("input"); qty.type="number"; qty.min="1"; qty.step="1"; qty.value=entry.qty; qty.setAttribute("aria-label", `${entry.name} miktarı`); qty.style.width="80px";
      qty.onchange = () => { entry.qty = Number(qty.value); requestId = null; };
      const remove = document.createElement("button"); remove.textContent="Çıkar"; remove.className="btn btn-sm btn-default"; remove.onclick=()=>{cart.delete(code);requestId=null;renderCart();};
      row.append(name,qty,remove);root.append(row);
    }
    if (!cart.size) root.textContent="Sepetiniz boş.";
  };
  const search = () => frappe.call({method:"cari_custom.portal.catalog",args:{search:document.getElementById("cari-search").value}}).then(({message})=>{
    const root=document.getElementById("cari-products");root.replaceChildren();
    for(const item of message.items){
      const card=document.createElement("article");card.className="cari-product";
      if(item.image){const img=document.createElement("img");img.src=item.image;img.alt=item.name;img.loading="lazy";card.append(img);}
      const title=document.createElement("h3");title.textContent=item.name;
      const code=document.createElement("small");code.textContent=`${item.item_code} · ${item.category} · ${item.uom}`;
      const price=document.createElement("strong");price.textContent=money(item.price,item.currency);
      const button=document.createElement("button");button.textContent=item.in_stock?"Sepete Ekle":"Stokta Yok";button.disabled=!item.in_stock;
      button.onclick=()=>{const old=cart.get(item.item_code);cart.set(item.item_code,{name:item.name,qty:old?old.qty+1:1});requestId=null;renderCart();};
      card.append(title,code,price,button);root.append(card);
    }
    status(message.items.length?"Fiyatlar KDV hariçtir.":"Gösterilecek ürün yok.");
  });
  document.getElementById("cari-search-button").onclick=search;
  document.getElementById("cari-order").onclick=()=>{
    if(!cart.size){status("Sepete ürün ekleyin.");return;}
    if(frappe.session.user === "Guest"){window.location.assign("/login?redirect-to=/cari-portal");return;}
    const items=[...cart].map(([item_code,row])=>({item_code,qty:row.qty}));
    requestId=requestId || crypto.randomUUID();
    const button=document.getElementById("cari-order");button.disabled=true;
    frappe.call({method:"cari_custom.portal.place_order",args:{items:JSON.stringify(items),request_id:requestId}}).then(({message})=>{
      status(`Sipariş ${message.name} onaya gönderildi. Toplam: ${money(message.grand_total,message.currency)}`);cart.clear();requestId=null;renderCart();
    }).finally(()=>{button.disabled=false;});
  };
  document.getElementById("cari-records-button").onclick=()=>{
    if(frappe.session.user === "Guest"){status("Kayıtlarınız için giriş yapın.");return;}
    frappe.call({method:"cari_custom.portal.my_records",args:{kind:document.getElementById("cari-kind").value}}).then(({message:rows})=>{
      const root=document.getElementById("cari-records");root.replaceChildren();
      if(!rows.length){root.textContent="Bu türde kayıt yok.";return;}
      const table=document.createElement("table");const keys=Object.keys(rows[0]);const header=table.createTHead().insertRow();
      for(const key of keys){const th=document.createElement("th");th.textContent=key;header.append(th);}
      const body=table.createTBody();for(const record of rows){const row=body.insertRow();for(const key of keys)row.insertCell().textContent=record[key] ?? "—";}
      root.append(table);
    });
  };
  renderCart();search();
});
