(() => {
  const corrections = {
    pg006_n0007: 'Lengo la kitabu hiki ni kukuza uwezo wako wa kuzungumza, kusikiliza, kutumia lugha ya alama katika mawasiliano, kusoma na kuandika lugha ya Kiswahili.',
    pg027_n0026: 'Simulia kwa maneno yako mwenyewe / tumia lugha ya alama kuelezea tukio ulilosoma kwa kuzingatia nyakati sahihi.',
    pg046_n0028: 'Simulia / tumia lugha ya alama kuelezea mbele ya darasa tukio lolote la kufurahisha au kusikitisha ulilowahi kushuhudia; kisha ruhusu maswali kutoka kwa wanafunzi wenzako na uyajibu.',
    pg061_n0015: 'Simulia kwa maneno yako mwenyewe / tumia lugha ya alama kuelezea hadithi uliyoisoma.',
    pg079_n0016: 'Msomee mwenzako hadithi / tumia lugha ya alama kumwelezea mwenzako hadithi, kisha jibu maswali yanayofuata.',
    pg080_n0032: 'Sikiliza milio / igiza milio na kuonesha kwa kutumia lugha ya alama wanyama na vitu vifuatavyo.',
    pg081_n0005: 'Kwa kuongozwa na mwalimu, sikiliza / tazama video ya hadithi yoyote kutoka katika vyanzo mbalimbali vya TEHAMA.',
    pg081_n0010: 'Kisha msimulie / tumia lugha ya alama kumwelezea mwenzako hadithi hiyo, na pendekeza jina la hadithi hiyo.',
    pg082_n0004: 'Kusimulia / kutumia lugha ya alama kuelezea hadithi',
    pg090_n0065: 'Simulia / tumia lugha ya alama kuelezea hadithi fupi kuhusu kuku na mwewe.',
    pg091_n0007: 'Vilevile, utaandika na kusimulia / kutumia lugha ya alama kuelezea hadithi.',
    pg099_n0011: 'Andika hadithi yenye maneno sabini (70), kisha msimulie mwenzako / tumia lugha ya alama kumwelezea mwenzako.',
    pg100_n0008: 'Aidha, utasimulia / kutumia lugha ya alama kuelezea hadithi kwa kuanza na mianzo na kumalizia na miisho uliyojifunza.',
    pg115_n0036: 'Imba wimbo huu kwa sauti / tumia lugha ya alama kusoma wimbo huu, kisha andika haki za mtoto zilizotajwa.',
    pg118_n0009: 'Umahiri utakaoujenga utakuwezesha kuwasiliana kwa kutumia semi mbalimbali katika mazungumzo, lugha ya alama na maandishi katika miktadha mbalimbali.',
    pg128_n0007: 'Umahiri utakaoujenga utakuwezesha kuwasilisha hoja kwa njia ya mazungumzo / lugha ya alama katika miktadha mbalimbali.',
    pg007_n0008: 'Umahiri utakaoujenga utakuwezesha kulinganisha vitu kwa kuzingatia sifa za vitu hivyo katika mazungumzo, kwa lugha ya alama na maandishi ya kila siku.',
    pg027_n0029: 'Igiza na wenzako / tumia lugha ya alama kuwasilisha mazungumzo kati ya Mwalimu Sara na Mwalimu Mbilo.',
    pg028_n0010: 'Umahiri utakaoujenga utakuwezesha kutumia hali timilifu na ya mazoea katika mazungumzo, lugha ya alama na maandishi ya kila siku.',
    pg038_n0010: 'Umahiri utakaoujenga utakuwezesha kujieleza kwa kujiamini na kuanzisha na kuendeleza mazungumzo kwa sauti, lugha ya alama au maandishi katika mazingira mbalimbali.',
    pg047_n0009: 'Sura hii itakujengea umahiri wa kutumia vitendawili, nahau na methali katika mazungumzo, lugha ya alama na maandishi ya kila siku.',
    pg047_n0012: 'Umahiri utakaoujenga utakuwezesha kutumia vitendawili, nahau na methali katika mazungumzo, lugha ya alama na maandishi ya kila siku.',
    pg073_n0003: 'Kusikiliza / kutazama video ya hadithi',
    pg073_n0007: 'Katika sura hii, utajifunza namna ya kusikiliza / kutazama video ya hadithi na kuisimulia / kutumia lugha ya alama kuelezea hadithi hiyo.',
    pg073_n0026: 'Sikiliza / tazama video ya hadithi, kisha jibu maswali yanayofuata.',
    pg075_n0050: 'Simulia / tumia lugha ya alama kuelezea hadithi uliyoisoma.',
    pg080_n0029: 'Mwandikie mwenzako maelezo ya kuchora picha tano, kisha msomee / tumia lugha ya alama kumwelezea ili achore picha hizo.',
    pg082_n0007: 'Katika sura hii, utajifunza kusimulia / kutumia lugha ya alama kuelezea hadithi mbalimbali kwa kuzingatia hisia ili kuwavutia wasikilizaji au watazamaji.',
    pg082_n0008: 'Vilevile, utajifunza kubaini hisia za msimuliaji au anayetumia lugha ya alama na za msikilizaji au mtazamaji.',
    pg082_n0009: 'Umahiri utakaoujenga utakuwezesha kusimulia / kutumia lugha ya alama kuelezea matukio kwa hisia na kwa ufasaha.',
    pg086_n0009: 'Simulia kwa maneno yako mwenyewe / tumia lugha ya alama kuelezea hadithi uliyoisoma.',
    pg100_n0009: 'Umahiri utakaoujenga utakuwezesha kutumia mianzo na miisho ya hadithi mbalimbali katika kusimulia / kutumia lugha ya alama kuelezea hadithi na kuwavutia wasikilizaji au watazamaji.'
  };

  const tocEntries = {
    pg004_n0005: ['Kusikiliza/kutazama video ya hadithi', '67', 'Kusikiliza au kutazama video ya hadithi'],
    pg004_n0009: ['Kusimulia hadithi/kutumia Lugha ya alama kuelezea hadithi', '76', 'Kusimulia hadithi au kutumia Lugha ya alama kuelezea hadithi'],
    pg004_n0013: ['Kuandika hadithi', '85', 'Kuandika hadithi'],
    pg004_n0017: ['Mianzo na miisho ya hadithi', '94', 'Mianzo na miisho ya hadithi'],
    pg004_n0021: ['Kusoma kwa ufasaha na ufahamu', '104', 'Kusoma kwa ufasaha na ufahamu'],
    pg004_n0025: ['Kutumia semi katika mawasiliano', '112', 'Kutumia semi katika mawasiliano'],
    pg004_n0029: ['Kujenga na kuwasilisha hoja', '122', 'Kujenga na kuwasilisha hoja']
  };

  const arrangeTocEntries = () => {
    for (const [id, [label, page, spokenLabel]] of Object.entries(tocEntries)) {
      const target = document.querySelector(`[data-id="${id}"]`);
      if (!target) continue;
      if (id === 'pg004_n0009') {
        const lines = target.querySelectorAll(':scope > span');
        const firstLine = lines[0]?.textContent?.trim();
        const secondLine = lines[1]?.textContent?.replace(/\s+/g, '').trim();
        if (
          target.dataset.tocLayout === 'two-line' &&
          lines.length === 2 &&
          firstLine === 'Kusimulia hadithi/kutumia Lugha ya alama' &&
          secondLine === 'kuelezeahadithi76'
        ) continue;
        target.dataset.tocLayout = 'two-line';
        target.setAttribute('aria-label', `${spokenLabel}, ukurasa wa ${page}`);
        target.className = 'w-full min-w-0 text-[26px] leading-snug max-lg:text-[20px] max-sm:text-[17px]';
        target.innerHTML = '<span class="block">Kusimulia hadithi/kutumia Lugha ya alama</span><span class="flex w-full min-w-0 items-end"><span class="shrink-0">kuelezea hadithi</span><span aria-hidden="true" class="mx-3 mb-[7px] min-w-[2rem] flex-1 border-b-[3px] border-dotted border-zinc-700"></span><span class="shrink-0">76</span></span>';
        continue;
      }
      const parts = target.querySelectorAll(':scope > span');
      if (target.dataset.tocLayout === 'responsive' && parts.length === 3 && parts[0].textContent === label && parts[2].textContent === page) continue;
      target.dataset.tocLayout = 'responsive';
      target.setAttribute('aria-label', `${spokenLabel}, ukurasa wa ${page}`);
      target.className = 'flex w-full min-w-0 items-end text-[26px] leading-snug max-lg:text-[20px] max-sm:text-[17px]';
      target.innerHTML = `<span class="min-w-0">${label}</span><span aria-hidden="true" class="mx-3 mb-[7px] min-w-[2rem] flex-1 border-b-[3px] border-dotted border-zinc-700"></span><span class="shrink-0">${page}</span>`;
    }
  };

  const options = {};

  const removeDuplicateBlocks = () => {
    const pageId = document.querySelector('meta[name="title-id"]')?.content;
    if (pageId === 'pg087_sec001') {
      document.querySelector('[aria-labelledby="pg087-cont"]')?.remove();
    }
    if (pageId === 'pg088_sec001') {
      document.querySelector('[aria-labelledby="pg088-cont"]')?.remove();
    }
  };

  const apply = () => {
    removeDuplicateBlocks();
    arrangeTocEntries();

    for (const [id, text] of Object.entries(corrections)) {
      const target = document.querySelector(`[data-id="${id}"]`);
      if (target && target.textContent !== text) target.textContent = text;
    }

    for (const [id, text] of Object.entries(options)) {
      const source = document.querySelector(`[data-id="${id}"]`);
      if (!source || document.querySelector(`[data-inclusive-for="${id}"]`)) continue;
      const addition = document.createElement('span');
      addition.dataset.inclusiveFor = id;
      addition.className = 'adt-inclusive-option font-semibold text-emerald-800';
      addition.setAttribute('role', 'note');
      addition.setAttribute('tabindex', '0');
      addition.textContent = text;
      addition.setAttribute('aria-label', `Chaguo jumuishi${text.replace(/^\s*\/\s*/, ': ')}`);
      source.insertAdjacentElement('afterend', addition);
    }
  };

  apply();
  window.addEventListener('adt:languageChanged', apply);
  new MutationObserver(apply).observe(document.body, { childList: true, subtree: true });
})();
