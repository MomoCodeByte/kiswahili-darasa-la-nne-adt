(function () {
  "use strict";

  const styleChoice = (label, selected) => {
    label.style.display = "inline-flex";
    label.style.alignItems = "center";
    label.style.gap = "0.5rem";
    label.style.padding = "0.55rem 0.9rem";
    label.style.border = `2px solid ${selected ? "#1d4ed8" : "#94a3b8"}`;
    label.style.borderRadius = "0.75rem";
    label.style.background = selected ? "#dbeafe" : "#ffffff";
    label.style.fontWeight = selected ? "700" : "600";
    label.style.cursor = "pointer";
    label.setAttribute("aria-pressed", selected ? "true" : "false");
  };

  const revealTrueFalseControls = () => {
    document
      .querySelectorAll('section[data-section-type="activity_true_false"] fieldset')
      .forEach((fieldset) => {
        const radios = Array.from(
          fieldset.querySelectorAll('input[type="radio"][data-activity-item]'),
        );
        if (!radios.length) return;

        const hiddenContainer = radios[0].closest("div.sr-only");
        if (hiddenContainer) {
          hiddenContainer.classList.remove("sr-only");
          hiddenContainer.style.display = "flex";
          hiddenContainer.style.flexWrap = "wrap";
          hiddenContainer.style.gap = "0.75rem";
          hiddenContainer.style.marginTop = "0.65rem";
          hiddenContainer.style.marginLeft = "3.5rem";
        }

        const updateChoices = () => {
          radios.forEach((radio) => {
            const label =
              fieldset.querySelector(`label[for="${CSS.escape(radio.id)}"]`) ||
              radio.closest("label");
            if (label) styleChoice(label, radio.checked);
          });
        };

        radios.forEach((radio) => {
          const label =
            fieldset.querySelector(`label[for="${CSS.escape(radio.id)}"]`) ||
            radio.closest("label");
          radio.classList.remove("sr-only", "peer");
          radio.style.width = "1.15rem";
          radio.style.height = "1.15rem";
          radio.style.accentColor = "#1d4ed8";
          if (label && !label.contains(radio)) label.prepend(radio);
          radio.addEventListener("change", updateChoices);
        });
        updateChoices();
      });
  };

  const materializePage94TextInputs = () => {
    const section = document.querySelector('[data-section-id="pg077_sec001"]');
    const heading = section?.querySelector('[data-id="pg077_n0023"]');
    const sectionB = heading?.closest(".space-y-4");
    if (!sectionB) return;

    const rows = Array.from(sectionB.querySelectorAll(".space-y-2 > div.flex"));
    const blankLines = rows
      .map((row) => row.querySelector('span[aria-hidden="true"]'))
      .filter(Boolean);
    if (blankLines.length !== 8) return;

    const answers = {};
    blankLines.forEach((blankLine, index) => {
      const item = `item-${index + 6}`;
      const word = rows[index].querySelector("[data-id]")?.textContent?.trim() || "";
      const input = document.createElement("input");
      input.type = "text";
      input.dataset.ariaId = `aria-page94-${index}`;
      input.dataset.activityItem = item;
      input.setAttribute("aria-label", `Jibu la ${word || index + 1}`);
      input.tabIndex = 0;
      input.className =
        "flex-1 min-w-24 border-0 border-b-2 border-gray-700 bg-transparent px-2 outline-none focus:border-sky-600";
      blankLine.replaceWith(input);
      answers[item] = "";
    });
    window.correctAnswers = Object.assign({}, window.correctAnswers || {}, answers);
  };

  materializePage94TextInputs();
  revealTrueFalseControls();
})();
