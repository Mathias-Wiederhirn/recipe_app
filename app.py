import streamlit as st
import math
import streamlit.components.v1 as components
from utils import search_recipes
from generate_pdf import create_shopping_list_pdf

# --- Page config ---
st.set_page_config(page_title="Bella Papaya Recipe Search", page_icon="🍽️", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.title("🍽️ Bella Papaya Recipe Search")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# --- Session state ---
if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = []
if "recipe_results" not in st.session_state:
    st.session_state.recipe_results = []

# --- Search form ---
with st.form("search_form"):
    query = st.text_input("🔍 Enter a keyword (e.g., egg, chicken, pasta):", placeholder="egg")

    meal_types = ["🍽️ Any", "🍳 Breakfast", "🥪 Lunch", "🍝 Dinner", "🍪 Snack"]
    meal_type_selection = st.selectbox("🏷️ Select Meal Type", meal_types)
    meal_type_clean = meal_type_selection.split(" ", 1)[-1].lower()
    meal_type = None if "any" in meal_type_clean else meal_type_clean

    gluten_free = st.toggle("🌾 Gluten-Free Only")
    max_calories = st.slider("Max Calories (kcal)", 100, 1500, 1000, step=50)
    min_protein = st.slider("Min Protein (g)", 0, 100, 5, step=5)
    count = st.slider("Number of recipes to show", 1, 20, 10)

    submitted = st.form_submit_button("Search")

# --- Handle empty input ---
if submitted and not query.strip():
    st.warning("🔎 Please enter a keyword to search for recipes!")

# --- Handle search ---
elif submitted:
    health = "gluten-free" if gluten_free else None
    results = search_recipes(query, meal_type, None, health, count * 2)

    filtered = []
    for recipe in results:
        calories = recipe.get("calories", 0)
        protein = recipe.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0)
        if calories <= max_calories and protein >= min_protein:
            filtered.append(recipe)
        if len(filtered) >= count:
            break

    if not filtered:
        st.info(f"😕 No recipes found for **{query}**. Try a different keyword!")
    else:
        st.session_state.recipe_results = filtered

# --- Display results ---
if st.session_state.recipe_results:
    st.subheader("🍲 Recipes")

    cols_per_row = 3
    total = len(st.session_state.recipe_results)
    rows = math.ceil(total / cols_per_row)

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            idx = row * cols_per_row + col_idx
            if idx >= total:
                break

            recipe = st.session_state.recipe_results[idx]
            title = recipe.get("label", "No title")
            image_url = recipe.get("image", "")
            calories = int(recipe.get("calories", 0))
            protein = int(recipe.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0))
            url = recipe.get("url", "#")
            ingredients = recipe.get("ingredientLines", [])

            with cols[col_idx]:
                st.markdown(f"""
                    <div style="
                        border: 1px solid #ddd;
                        border-radius: 12px;
                        padding: 1.2em;
                        margin-bottom: 20px;
                        background: linear-gradient(to bottom right, #ffffff, #f9f9f9);
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    ">
                        <h4 style=\"color:#2E86C1; margin-top:0;\">{title}</h4>
                        <img src=\"{image_url}\" style=\"width:100%; border-radius:10px; margin-bottom:1em;\" />
                        <p style=\"font-size: 0.9em; margin: 4px 0;\"><strong>Calories:</strong> {calories} kcal</p>
                        <p style=\"font-size: 0.9em; margin: 4px 0;\"><strong>Protein:</strong> {protein:.1f} g</p>
                        <a href=\"{url}\" target=\"_blank\" style=\"
                            display: inline-block;
                            padding: 8px 16px;
                            background: linear-gradient(135deg, #2980b9, #3498db);
                            color: white;
                            border-radius: 8px;
                            text-decoration: none;
                            font-size: 0.9em;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                            transition: background 0.3s ease, transform 0.2s ease;
                        \" onmouseover=\"this.style.transform='scale(1.05)'\" onmouseout=\"this.style.transform='scale(1)'\">
                            View Full Recipe
                        </a>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("➕ Add to Shopping List", key=f"add_{idx}"):
                    st.session_state.shopping_list.append((title, ingredients))
                    st.success(f"✅ Ingredients from '{title}' added! [🛒 Go to Shopping List](#shopping-list)")

# --- Floating Top Button ---
st.markdown("""
<style>
.top-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    display: block;
    padding: 10px 12px;
    background: linear-gradient(135deg, #2980b9, #3498db);
    color: white;
    border-radius: 6px;
    text-decoration: none;
    font-size: 1.2em;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    transition: background 0.3s ease, transform 0.2s ease;
    z-index: 9999;
}
.top-button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #3498db, #2980b9);
}

/* Show button on scroll */
<script>
window.addEventListener('scroll', function() {
  const btn = document.querySelector('.top-button');
  if (window.scrollY > 300) {
    btn.style.display = 'inline-block';
  } else {
    btn.style.display = 'none';
  }
});
</script>
</style>
<a href="#top" class="top-button">⬆️</a>
""", unsafe_allow_html=True)

# --- Shopping List section ---
if st.session_state.shopping_list:
    st.markdown("---")
    st.markdown('<h2 id="shopping-list">🛒 Shopping List</h2>', unsafe_allow_html=True)

    for title, ingredients in st.session_state.shopping_list:
        st.markdown(f"**{title}**")
        for item in ingredients:
            st.markdown(f"• {item}")

    col1, col2 = st.columns([1, 1])

    with col1:
        pdf_path = create_shopping_list_pdf(
            st.session_state.shopping_list,
            "shopping_list.pdf"
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Shopping List (PDF)",
                data=f,
                file_name="shopping_list.pdf",
                mime="application/pdf"
            )

    with col2:
        if st.button("🗑️ Clear Shopping List"):
            st.session_state.shopping_list = []
            st.success("🧹 Shopping list cleared.")
            st.rerun()

# --- Back to Top Button ---
components.html("""
<style>
#scrollTopBtn {
  display: none;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-size: 20px;
  background: linear-gradient(135deg, #2980b9, #3498db);
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}
#scrollTopBtn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #3498db, #2980b9);
}
</style>

<button onclick=\"topFunction()\" id=\"scrollTopBtn\">⬆️</button>

<script>
function topFunction() {
    window.scrollTo({top: 0, behavior: 'smooth'});
}
</script>
""", height=100)

# --- Back to Top Button ---
components.html("""
<style>
#scrollTopBtn {
  display: none;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-size: 18px;
  background: linear-gradient(135deg, #2980b9, #3498db);
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}
#scrollTopBtn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #3498db, #2980b9);
}
</style>

<button onclick=\"topFunction()\" id=\"scrollTopBtn\">⬆️</button>

<script>
const scrollBtn = document.getElementById(\"scrollTopBtn\");
window.onscroll = function() {
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        scrollBtn.style.display = \"block\";
    } else {
        scrollBtn.style.display = \"none\";
    }
};
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
</script>
""", height=0)
