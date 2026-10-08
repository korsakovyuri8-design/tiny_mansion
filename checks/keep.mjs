/* Латиница, которой место в любом переводе: бренды, имена ферм и хозяев,
   химия, классы прав, стандарты, модели оборудования. Список общий для
   latin.mjs, который ищет непереведённое в русской версии по письму, и для
   untranslated.mjs, который ищет его во всех версиях по совпадению с
   английской строкой. Новое попадание это либо недостающий ключ словаря,
   либо термин, которому здесь место. */
export const KEEP = [
  /TINY MANSION/g, /Korsakov Group(\s+d\.o\.o\.)?/g, /Best Western/g,
  /\bI{1,3}V?\b/g,   /* Roman quarters: I, II, III, IV */
  /\bEN\b/g, /\bRU\b/g, /\bSR\b/g, /\bTR\b/g,
  /Grand Residence 24ft/g, /Residence 2\dft/g, /Trailer Made/g,
  /Đedov(ina|\s+Do)?/g, /Ravni/g, /Eko Oaza/g, /Karadžić/g, /Pavićević/g, /Pešić/g, /Medojević/g,
  /Victron/g, /Cerbo GX/g, /Nuki/g, /Orbital/g, /LiFePO[₄4]?/g, /Wyndham/g,
  /Instagram/g, /FormSubmit/g, /Google( Fonts)?/g, /La Marzocco( Linea)?/g,
  /Radisson( Individuals)?/g, /CO[₂2]/g, /\bIP\b/g, /Tiny Mansion/g, /Farm Store/g,
  /full-stack/gi, /white label/gi, /on-demand/gi, /Morsko dobro/g, /konoba/gi,
  /\bPIR\b/g, /\bCEE\b/g, /\bCE\b/g, /\bPOS\b/g, /\bR-\d+\b/g, /\bB96\b/g,
  /\bBE\b/g, /\bAV\b/g, /\bLED\b/g, /°C/g, /\bGX\b/g, /[\w.+-]+@[\w.-]+/g, /e-?mail/gi,
  /Charming Pony Village House/g, /Bijelo Polje/g, /Mojkovac/g, /Nikšić/g,
  /Dobrilovina/g, /Žabljak/g, /Durmitor/g, /Biogradska/g, /Crmnica/g, /Bojna Njiva/g,
  /Yuri Korsakov/g, /Sergei Ermakov/g, /Nana Tabidze/g, /Aleksan Vartapetyan/g,
  /Draft & Craft Bar/g, /Espresso & Cocktail Lounge/g,
  /Espresso bar/g,   /* по-турецки пишется так же, как по-английски */
];
export const strip = t => KEEP.reduce((s, r) => s.replace(r, ''), t);
