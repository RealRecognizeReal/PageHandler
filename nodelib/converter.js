const texzilla = require('./TexZilla.min.js');
var mathml = texzilla.toMathMLString(process.argv[2]);
console.log(mathml);
