---
title: Macro Calculator
description: Calculate your daily calorie and macronutrient needs for muscle gain, fat loss, or maintenance. Science-backed formulas.
---

<style>
.calc-wrap { max-width: 900px; margin: 0 auto; }
.calc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
@media (max-width: 768px) { .calc-grid { grid-template-columns: 1fr; } }
.calc-form { background: var(--color-card-bg, #fff); border-radius: 12px; padding: 1.5rem; border: 1px solid var(--color-border, #e5e7eb); }
.calc-form label { display: block; font-weight: 600; margin-bottom: 0.25rem; font-size: 0.9rem; color: var(--color-text, #1f2937); }
.calc-form .field { margin-bottom: 1.25rem; }
.calc-form select, .calc-form input[type="number"] { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid var(--color-border, #d1d5db); border-radius: 8px; font-size: 1rem; background: var(--color-bg, #fff); color: var(--color-text, #1f2937); box-sizing: border-box; }
.calc-form select:focus, .calc-form input:focus { outline: none; border-color: #f97316; box-shadow: 0 0 0 3px rgba(249,115,22,0.15); }
.calc-form .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.calc-form .radio-group { display: flex; gap: 0.5rem; }
.calc-form .radio-group label { font-weight: 400; font-size: 0.85rem; display: flex; align-items: center; gap: 0.3rem; cursor: pointer; padding: 0.4rem 0.75rem; border: 1px solid var(--color-border, #d1d5db); border-radius: 8px; }
.calc-form .radio-group input:checked + label { background: #f97316; color: #fff; border-color: #f97316; }
#calc-btn-wrap { margin-top: 1.5rem; }
#calc-btn { width: 100%; padding: 1.25rem 1rem; background: linear-gradient(135deg, #f97316, #ea580c); color: #fff; border: none; border-radius: 12px; font-size: 1.35rem; font-weight: 800; cursor: pointer; transition: all 0.2s; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(249,115,22,0.35); }
#calc-btn:hover { background: linear-gradient(135deg, #ea580c, #dc2626); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(249,115,22,0.45); }
#calc-btn:active { transform: translateY(0); }
.calc-results { background: linear-gradient(135deg, #1a1a2e 0%, #2d1b00 100%); border-radius: 12px; padding: 1.5rem; color: #fff; }
.calc-results h3 { color: #fff; margin-top: 0; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 0.75rem; margin-bottom: 1rem; }
.calorie-display { text-align: center; padding: 1.5rem 0; }
.calorie-display .number { font-size: 3.5rem; font-weight: 900; color: #f97316; line-height: 1; }
.calorie-display .label { font-size: 0.9rem; opacity: 0.7; margin-top: 0.25rem; }
.macro-bars { margin-top: 1rem; }
.macro-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }
.macro-row .macro-label { width: 70px; font-size: 0.85rem; font-weight: 600; }
.macro-row .macro-bar-wrap { flex: 1; height: 28px; background: rgba(255,255,255,0.1); border-radius: 14px; overflow: hidden; position: relative; }
.macro-row .macro-bar { height: 100%; border-radius: 14px; transition: width 0.3s ease; }
.macro-row .macro-bar.protein { background: #f97316; }
.macro-row .macro-bar.carbs { background: #3b82f6; }
.macro-row .macro-bar.fat { background: #a855f7; }
.macro-row .macro-grams { width: 80px; text-align: right; font-size: 0.85rem; font-weight: 600; }
.macro-row .macro-percent { width: 40px; text-align: right; font-size: 0.75rem; opacity: 0.6; }
.calc-results .meal-suggestion { margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.15); }
.calc-results .meal-suggestion p { font-size: 0.85rem; opacity: 0.8; margin: 0.3rem 0; }
.calc-results .meal-suggestion strong { color: #f97316; }
@media (max-width: 768px) { .calorie-display .number { font-size: 2.5rem; } }
</style>

<div class="calc-wrap">

<div class="calc-grid">

<div class="calc-form">

<div class="field">
<label for="age">Age</label>
<input type="number" id="age" value="30" min="10" max="100">
</div>

<div class="field">
<label>Sex</label>
<div class="radio-group" id="sex-group">
<input type="radio" name="sex" id="sex-male" value="male" checked hidden>
<label for="sex-male">&#9794; Male</label>
<input type="radio" name="sex" id="sex-female" value="female" hidden>
<label for="sex-female">&#9792; Female</label>
</div>
</div>

<div class="row">
<div class="field">
<label for="weight">Weight</label>
<input type="number" id="weight" value="80" min="20" max="300" step="0.1">
</div>
<div class="field">
<label for="weight-unit">Unit</label>
<select id="weight-unit"><option value="kg">kg</option><option value="lbs">lbs</option></select>
</div>
</div>

<div class="row">
<div class="field">
<label for="height">Height</label>
<input type="number" id="height" value="178" min="50" max="280">
</div>
<div class="field">
<label for="height-unit">Unit</label>
<select id="height-unit"><option value="cm">cm</option><option value="ft">ft</option></select>
</div>
</div>

<div class="field">
<label for="activity">Activity Level</label>
<select id="activity">
<option value="1.2">Sedentary (desk job, no exercise)</option>
<option value="1.375">Light (1–3 days/week)</option>
<option value="1.55" selected>Moderate (3–5 days/week)</option>
<option value="1.725">Active (6–7 days/week)</option>
<option value="1.9">Very Active (2x/day or physical job)</option>
</select>
</div>

<div class="field">
<label for="goal">Goal</label>
<select id="goal">
<option value="lose">Lose Weight</option>
<option value="maintain" selected>Maintain</option>
<option value="gain">Gain Muscle</option>
</select>
</div>

<div id="calc-btn-wrap">
<button id="calc-btn">Calculate My Macros</button>
</div>
</div>

<div class="calc-results" id="results">
<h3>Your Daily Targets</h3>
<div class="calorie-display">
<div class="number" id="calories-output">2,500</div>
<div class="label">calories per day</div>
</div>
<div class="macro-bars">
<div class="macro-row">
<span class="macro-label" style="color:#f97316">Protein</span>
<div class="macro-bar-wrap"><div class="macro-bar protein" id="protein-bar" style="width:30%"></div></div>
<span class="macro-grams" id="protein-grams">188g</span>
<span class="macro-percent" id="protein-pct">30%</span>
</div>
<div class="macro-row">
<span class="macro-label" style="color:#3b82f6">Carbs</span>
<div class="macro-bar-wrap"><div class="macro-bar carbs" id="carbs-bar" style="width:40%"></div></div>
<span class="macro-grams" id="carbs-grams">250g</span>
<span class="macro-percent" id="carbs-pct">40%</span>
</div>
<div class="macro-row">
<span class="macro-label" style="color:#a855f7">Fat</span>
<div class="macro-bar-wrap"><div class="macro-bar fat" id="fat-bar" style="width:30%"></div></div>
<span class="macro-grams" id="fat-grams">83g</span>
<span class="macro-percent" id="fat-pct">30%</span>
</div>
</div>
<div class="meal-suggestion" id="meal-suggestion"></div>
</div>

</div>

</div>

<script>
(function() {
  function calculate() {
    var age = parseFloat(document.getElementById('age').value) || 30;
    var sexEl = document.querySelector('input[name="sex"]:checked');
    var isMale = sexEl ? sexEl.value === 'male' : true;
    var weight = parseFloat(document.getElementById('weight').value) || 80;
    var weightUnit = document.getElementById('weight-unit').value;
    var height = parseFloat(document.getElementById('height').value) || 178;
    var heightUnit = document.getElementById('height-unit').value;
    var activity = parseFloat(document.getElementById('activity').value) || 1.55;
    var goal = document.getElementById('goal').value;

    if (weightUnit === 'lbs') { weight = weight / 2.20462; }
    if (heightUnit === 'ft') { height = height * 30.48; }

    var bmr;
    if (isMale) {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }
    var tdee = bmr * activity;

    var cal, proteinPct, carbsPct, fatPct, mealIdea;
    if (goal === 'lose') {
      cal = tdee - 500;
      proteinPct = 0.40;
      carbsPct = 0.30;
      fatPct = 0.30;
      mealIdea = 'Try a high-protein breakfast (eggs + Greek yogurt) to stay full longer.';
    } else if (goal === 'gain') {
      cal = tdee + 300;
      proteinPct = 0.35;
      carbsPct = 0.40;
      fatPct = 0.25;
      mealIdea = 'Add an extra meal or shake — aim for 2g protein per kg of bodyweight.';
    } else {
      cal = tdee;
      proteinPct = 0.30;
      carbsPct = 0.40;
      fatPct = 0.30;
      mealIdea = 'Maintain balance: protein with every meal, prioritize whole food carbs.';
    }

    var proteinG = Math.round((cal * proteinPct) / 4);
    var carbsG = Math.round((cal * carbsPct) / 4);
    var fatG = Math.round((cal * fatPct) / 9);

    document.getElementById('calories-output').textContent = Math.round(cal).toLocaleString();
    document.getElementById('protein-grams').textContent = proteinG + 'g';
    document.getElementById('carbs-grams').textContent = carbsG + 'g';
    document.getElementById('fat-grams').textContent = fatG + 'g';
    document.getElementById('protein-pct').textContent = Math.round(proteinPct * 100) + '%';
    document.getElementById('carbs-pct').textContent = Math.round(carbsPct * 100) + '%';
    document.getElementById('fat-pct').textContent = Math.round(fatPct * 100) + '%';
    document.getElementById('protein-bar').style.width = Math.round(proteinPct * 100) + '%';
    document.getElementById('carbs-bar').style.width = Math.round(carbsPct * 100) + '%';
    document.getElementById('fat-bar').style.width = Math.round(fatPct * 100) + '%';

    var mealEl = document.getElementById('meal-suggestion');
    mealEl.innerHTML = '<p><strong>Tip:</strong> ' + mealIdea + '</p>';
  }

  var btn = document.getElementById('calc-btn');
  if (btn) {
    btn.addEventListener('click', function() {
      calculate();
      btn.textContent = 'Calculated!';
      setTimeout(function() {
        btn.textContent = 'Calculate My Macros';
      }, 2000);
    });
  }

  calculate();
})();
</script>
