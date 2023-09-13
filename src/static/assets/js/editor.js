function run() {
    var text = document.getElementById('sourceTA').value,
    target = document.getElementById('targetDiv'),
    converter = new showdown.Converter(),
    html = converter.makeHtml(text);
  
    console.log(html);
    target.innerHTML = html;
  }
function print() {
    var text = document.getElementById('sourceTA').value;
    converter = new showdown.Converter();
    var html = converter.makeHtml(text);
    var janelaImpressao = window.open('', '', 'width=800, height=600');
    
    janelaImpressao.document.open();
    janelaImpressao.document.write('<html><head><title>Threat Copilot - Modelo de Ameaças</title></head><body>');
    janelaImpressao.document.write(html);
    janelaImpressao.document.write('</body></html>');
    
    janelaImpressao.document.close();
    janelaImpressao.print();
    janelaImpressao.close();
}

function save() {
  var text = document.getElementById('sourceTA').value;
  var linkDeDownload = document.createElement('a');
  var blob = new Blob([text], { type: 'text/plain' });
  linkDeDownload.href = URL.createObjectURL(blob);
  linkDeDownload.download = 'threat_modeling.md';
  linkDeDownload.click();
}