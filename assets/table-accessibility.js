(function () {
  "use strict";

  const ones = {
    1: "moja", 2: "mbili", 3: "tatu", 4: "nne", 5: "tano",
    6: "sita", 7: "saba", 8: "nane", 9: "tisa", 10: "kumi",
  };
  const tens = { 20: "ishirini", 30: "thelathini", 40: "arobaini", 50: "hamsini" };
  const numberWord = (number) => {
    if (ones[number]) return ones[number];
    if (number > 10 && number < 20) return `kumi na ${ones[number - 10]}`;
    if (number >= 20 && number < 60) {
      const base = number - (number % 10);
      return number === base ? tens[base] : `${tens[base]} na ${ones[number - base]}`;
    }
    return String(number);
  };
  const ordinal = (number) => ({ 1: "kwanza", 2: "pili", 3: "tatu" })[number] || numberWord(number);
  const rowCount = (number) => {
    if (number === 1) return "mstari mmoja";
    const agreements = { 2: "miwili", 3: "mitatu", 4: "minne", 5: "mitano" };
    return `mistari ${agreements[number] || numberWord(number)}`;
  };
  const columnCountPhrase = (number) => number === 1 ? "safu moja" : `safu ${numberWord(number)}`;

  const tables = Array.from(document.querySelectorAll("table"));
  tables.forEach((table, tableIndex) => {
    const rows = Array.from(table.rows);
    const occupied = new Set();
    const placements = [];
    let columnTotal = 0;
    rows.forEach((row, rowIndex) => {
      let column = 1;
      Array.from(row.cells).forEach((cell) => {
        while (occupied.has(`${rowIndex + 1}:${column}`)) column += 1;
        const columnSpan = Math.max(1, cell.colSpan || 1);
        const rowSpan = Math.max(1, cell.rowSpan || 1);
        placements.push({ cell, row: rowIndex + 1, column });
        for (let rowOffset = 0; rowOffset < rowSpan; rowOffset += 1) {
          for (let columnOffset = 0; columnOffset < columnSpan; columnOffset += 1) {
            occupied.add(`${rowIndex + 1 + rowOffset}:${column + columnOffset}`);
          }
        }
        columnTotal = Math.max(columnTotal, column + columnSpan - 1);
        column += columnSpan;
      });
    });

    const dimensions = `Jedwali lina ${rowCount(rows.length)} na ${columnCountPhrase(columnTotal)}`;
    if (table.hasAttribute("aria-label") || table.querySelector(":scope > caption")) {
      table.setAttribute("aria-description", dimensions);
    } else {
      table.setAttribute("aria-label", dimensions);
    }

    placements.forEach(({ cell, row, column }) => {
        const tableLabel = tables.length > 1 ? `Jedwali la ${ordinal(tableIndex + 1)}. ` : "";
        const location = `${tableLabel}Mstari wa ${ordinal(row)}, safu ya ${ordinal(column)}`;
        cell.querySelectorAll("input, textarea, select").forEach((control) => {
          const current = (control.getAttribute("aria-label") || "Andika jibu").trim();
          if (!current.startsWith(location)) {
            control.setAttribute("aria-label", `${location}. ${current}`);
          }
        });
    });
  });
})();
