function atualizar_candidato(resumo) {
  $("#nome").html(resumo['nome']);
  $("#partido").html(resumo['partido']);
  $("#unidade").html(resumo['uf']);
  $("#total").html(moeda(resumo['total']));
  $("#photo")[0].src=resumo['foto'];
}

function atualizar_doador(resumo) {
  $("#nome").html(resumo['nome']);
  $("#cpf_cnpj").html(resumo['cpf_cnpj']);
  $("#total").html(moeda(resumo['total']));
}

function atualizar_resumo(resumo) {
  $("#montante").html(moeda(resumo['montante']));
  $("#tot-candidatos").html(resumo['candidatos']);
}

function moeda(valor) {
  return "R$ " + valor.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&\,');
}

function clean(cpf_cnpj) {
 return cpf_cnpj.replace(/\.|\-|\//gi, '');
}

function update_chart(data) {
  var g = svg.selectAll(".arc")
             .data(pie(data))
             .enter().append("g")
                     .attr("class", "arc");

  g.append("path")
    .attr("d", arc)
    .on("mouseover", function(d) {
      $("#icone_selecionado").show();
      $("#doador_selecionado").html(d.data.doador.slice(0,15) + '...');
      $("#valor_selecionado").html(moeda(d.data.valor));
    })
    .on("mouseout", function(d) {
      $("#doador_selecionado").html("");
      $("#valor_selecionado").html("");
    })
    .style("fill", function(d, i) { return color(i); });
}
