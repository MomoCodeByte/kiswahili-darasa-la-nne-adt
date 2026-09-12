(function () {
  "use strict";

  const labels = {
    "item-1": "Mstari wa tano, safu ya tatu. Andika kipande cha mwisho kinachokamilisha sentensi",
    "item-2": "Swali la kwanza, safu ya wingi. Andika wingi wa neno kijiji",
    "item-3": "Swali la pili, safu ya wingi. Andika wingi wa neno eneo",
    "item-4": "Swali la tatu, safu ya umoja. Andika umoja wa neno miaka",
    "item-5": "Swali la nne, safu ya wingi. Andika wingi wa neno ardhi",
    "item-6": "Swali la tano, safu ya umoja. Andika umoja wa neno nyaya",
    "item-7": "Swali la sita, safu ya umoja. Andika umoja wa neno vikao",
    "item-8": "Swali la saba, safu ya wingi. Andika wingi wa neno jukumu",
    "item-9": "Swali la nane, safu ya wingi. Andika wingi wa neno zao",
    "item-10": "Swali la tisa, safu ya umoja. Andika umoja wa neno mahafali",
    "item-11": "Swali la kumi, safu ya wingi. Andika wingi wa neno mhitimu",
  };

  for (const [item, label] of Object.entries(labels)) {
    document.querySelector(`[data-activity-item="${item}"]`)?.setAttribute("aria-label", label);
  }
})();
