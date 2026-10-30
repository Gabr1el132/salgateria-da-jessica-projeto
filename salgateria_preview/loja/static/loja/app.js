(function () {
  // seletor de quantidade (+/-)
  document.querySelectorAll("[data-qtd]").forEach(function (box) {
    var input = box.querySelector("input");
    box.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        var min = +input.min || 1, max = +input.max || 999;
        input.value = Math.min(max, Math.max(min, (+input.value || min) + +b.dataset.d));
      });
    });
  });

  // mostrar/ocultar senha
  var olho = document.querySelector("[data-olho]");
  if (olho) olho.addEventListener("click", function () {
    var i = document.getElementById("id_password");
    i.type = i.type === "password" ? "text" : "password";
  });

  // tela de pagamento
  var f = document.getElementById("formpag");
  if (!f) return;
  var total = +f.dataset.total;
  var nomes = { dinheiro: "Dinheiro", pix: "Pix", cartao: "Cartão" };
  var campo = f.querySelector("[name=recebido]");
  var rapidos = f.querySelectorAll("[data-valor]");
  var fmt = function (c) {
    return "R$ " + (c / 100).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };
  var centavos = function (t) {
    var n = parseFloat(t.replace(/\./g, "").replace(",", "."));
    return isNaN(n) ? 0 : Math.round(n * 100);
  };
  function atualiza() {
    var forma = f.querySelector("[name=forma]:checked").value;
    f.querySelector("[data-dinheiro]").hidden = forma !== "dinheiro";
    f.querySelector("[data-forma]").textContent = nomes[forma];
    f.querySelectorAll(".opcao").forEach(function (o) {
      o.classList.toggle("sel", o.querySelector("input").checked);
    });
    var rec = centavos(campo.value), falta = rec < total;
    f.querySelector("[data-recebido]").textContent = fmt(rec);
    var troco = f.querySelector("[data-troco]");
    troco.textContent = !rec ? fmt(0) : falta ? "Faltam " + fmt(total - rec) : fmt(rec - total);
    troco.closest(".tile").classList.toggle("alerta", rec > 0 && falta);
    troco.closest(".tile").classList.toggle("verde", !(rec > 0 && falta));
    rapidos.forEach(function (c) { c.classList.toggle("sel", +c.dataset.valor === rec); });
  }
  rapidos.forEach(function (c) {
    c.addEventListener("click", function () {
      campo.value = (c.dataset.valor / 100).toFixed(2).replace(".", ",");
      atualiza();
    });
  });
  f.querySelectorAll("[name=forma]").forEach(function (r) { r.addEventListener("change", atualiza); });
  campo.addEventListener("input", atualiza);
  atualiza();
})();
