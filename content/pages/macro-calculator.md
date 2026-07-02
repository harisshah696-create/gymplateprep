---
title: Macro Calculator
description: Calculate your daily calorie and macronutrient needs for muscle gain, fat loss, or maintenance. Science-backed formulas.
---

<style>
.calc-wrap { max-width: 960px; margin: 0 auto; }
.calc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
@media (max-width: 768px) { .calc-grid { grid-template-columns: 1fr; } }

/* ─── Left Panel: Retro Form ─────────────────── */
.calc-form {
    background: #1a1b2e;
    border: 3px solid #ff2d78;
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 0 25px rgba(255, 45, 120, 0.25), inset 0 0 40px rgba(0, 0, 0, 0.3);
    position: relative;
}
.calc-form::before {
    content: '// INPUT';
    position: absolute;
    top: -11px;
    left: 16px;
    background: #1a1b2e;
    padding: 0 10px;
    font-size: 0.7rem;
    font-weight: 800;
    color: #00f5d4;
    letter-spacing: 2px;
    font-family: 'Courier New', monospace;
}
.calc-form label {
    display: block;
    font-weight: 700;
    margin-bottom: 0.3rem;
    font-size: 0.8rem;
    color: #00f5d4;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'Courier New', monospace;
}
.calc-form .field { margin-bottom: 1.1rem; }
.calc-form select,
.calc-form input[type="number"] {
    width: 100%;
    padding: 0.65rem 0.75rem;
    border: 2px solid #2a2b4a;
    border-radius: 10px;
    font-size: 1rem;
    background: #0f1023;
    color: #ff2d78;
    font-weight: 700;
    box-sizing: border-box;
    transition: border-color 0.2s, box-shadow 0.2s;
    font-family: 'Courier New', monospace;
}
.calc-form select:focus,
.calc-form input:focus {
    outline: none;
    border-color: #00f5d4;
    box-shadow: 0 0 12px rgba(0, 245, 212, 0.3);
}
.calc-form select option { background: #0f1023; color: #ff2d78; }
.calc-form .row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.calc-form .radio-group { display: flex; gap: 0.4rem; }
.calc-form .radio-group label {
    font-weight: 700;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    cursor: pointer;
    padding: 0.45rem 0.8rem;
    border: 2px solid #2a2b4a;
    border-radius: 10px;
    background: #0f1023;
    color: #6c6ea0;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s;
}
.calc-form .radio-group input:checked + label {
    background: #ff2d78;
    color: #fff;
    border-color: #ff2d78;
    box-shadow: 0 0 15px rgba(255, 45, 120, 0.4);
}

/* ─── Calculate Button ─────────────────────── */
#calc-btn-wrap { margin-top: 1.5rem; }
#calc-btn {
    width: 100%;
    padding: 1.1rem 1rem;
    background: linear-gradient(135deg, #ff2d78, #ff6b35);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: 900;
    cursor: pointer;
    transition: all 0.25s;
    letter-spacing: 2px;
    text-transform: uppercase;
    box-shadow: 0 0 20px rgba(255, 45, 120, 0.4);
    font-family: 'Courier New', monospace;
}
#calc-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 35px rgba(255, 45, 120, 0.6), 0 8px 25px rgba(255, 45, 120, 0.3);
}
#calc-btn:active { transform: translateY(0); }

/* ─── Right Panel: Retro Results ────────────── */
.calc-results {
    background: linear-gradient(145deg, #0f1023 0%, #1a1b2e 100%);
    border: 3px solid #00f5d4;
    border-radius: 16px;
    padding: 1.75rem;
    color: #fff;
    box-shadow: 0 0 25px rgba(0, 245, 212, 0.2), inset 0 0 40px rgba(0, 0, 0, 0.3);
    position: relative;
}
.calc-results::before {
    content: '// OUTPUT';
    position: absolute;
    top: -11px;
    left: 16px;
    background: #0f1023;
    padding: 0 10px;
    font-size: 0.7rem;
    font-weight: 800;
    color: #ff2d78;
    letter-spacing: 2px;
    font-family: 'Courier New', monospace;
}
.calc-results h3 {
    color: #00f5d4;
    margin: 0 0 0.75rem;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'Courier New', monospace;
    border-bottom: 2px solid rgba(0, 245, 212, 0.2);
    padding-bottom: 0.75rem;
}
.calorie-display {
    text-align: center;
    padding: 1.25rem 0;
}
.calorie-display .number {
    font-size: 3.75rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ff2d78, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    text-shadow: none;
    filter: drop-shadow(0 0 20px rgba(255, 45, 120, 0.4));
}
.calorie-display .label {
    font-size: 0.75rem;
    color: #6c6ea0;
    margin-top: 0.15rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'Courier New', monospace;
}

.macro-bars { margin-top: 1rem; }
.macro-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.65rem; }
.macro-row .macro-label {
    width: 65px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Courier New', monospace;
}
.macro-row .macro-bar-wrap {
    flex: 1;
    height: 22px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 11px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.macro-row .macro-bar {
    height: 100%;
    border-radius: 11px;
    transition: width 0.4s ease;
    position: relative;
}
.macro-row .macro-bar.protein {
    background: linear-gradient(90deg, #ff2d78, #ff6b35);
    box-shadow: 0 0 12px rgba(255, 45, 120, 0.4);
}
.macro-row .macro-bar.carbs {
    background: linear-gradient(90deg, #00f5d4, #00b4d8);
    box-shadow: 0 0 12px rgba(0, 245, 212, 0.4);
}
.macro-row .macro-bar.fat {
    background: linear-gradient(90deg, #a855f7, #d946ef);
    box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
}
.macro-row .macro-grams {
    width: 65px;
    text-align: right;
    font-size: 0.85rem;
    font-weight: 800;
    color: #fff;
    font-family: 'Courier New', monospace;
}
.macro-row .macro-percent {
    width: 35px;
    text-align: right;
    font-size: 0.7rem;
    color: #6c6ea0;
    font-family: 'Courier New', monospace;
}

.calc-results .meal-suggestion {
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 2px solid rgba(0, 245, 212, 0.15);
}
.calc-results .meal-suggestion p {
    font-size: 0.75rem;
    color: #6c6ea0;
    margin: 0.25rem 0;
    font-family: 'Courier New', monospace;
}
.calc-results .meal-suggestion strong { color: #00f5d4; }

@media (max-width: 768px) {
    .calorie-display .number { font-size: 2.75rem; }
    .calc-form, .calc-results { padding: 1.25rem; }
}
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
<div class="radio-group">
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
<label for="activity">Activity</label>
<select id="activity">
<option value="1.2">Sedentary</option>
<option value="1.375">Light (1-3 days)</option>
<option value="1.55" selected>Moderate (3-5 days)</option>
<option value="1.725">Active (6-7 days)</option>
<option value="1.9">Very Active (2x/day)</option>
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
<button id="calc-btn">Calculate</button>
</div>
</div>

<div class="calc-results" id="results">
<h3>Daily Targets</h3>
<div class="calorie-display">
<div class="number" id="calories-output">2,500</div>
<div class="label">calories</div>
</div>
<div class="macro-bars">
<div class="macro-row">
<span class="macro-label" style="color:#ff2d78">Protein</span>
<div class="macro-bar-wrap"><div class="macro-bar protein" id="protein-bar" style="width:30%"></div></div>
<span class="macro-grams" id="protein-grams">188g</span>
<span class="macro-percent" id="protein-pct">30%</span>
</div>
<div class="macro-row">
<span class="macro-label" style="color:#00f5d4">Carbs</span>
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
      mealIdea = 'High-protein breakfast (eggs + Greek yogurt) keeps you full.';
    } else if (goal === 'gain') {
      cal = tdee + 300;
      proteinPct = 0.35;
      carbsPct = 0.40;
      fatPct = 0.25;
      mealIdea = 'Add an extra meal or shake - 2g protein per kg bodyweight.';
    } else {
      cal = tdee;
      proteinPct = 0.30;
      carbsPct = 0.40;
      fatPct = 0.30;
      mealIdea = 'Protein with every meal, prioritize whole food carbs.';
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
    mealEl.innerHTML = '<p><strong>></strong> ' + mealIdea + '</p>';
  }

  var btn = document.getElementById('calc-btn');
  if (btn) {
    btn.addEventListener('click', function() {
      calculate();
      btn.textContent = '> CALCULATED';
      setTimeout(function() {
        btn.textContent = 'Calculate';
      }, 2000);
    });
  }

  calculate();
})();
</script>
