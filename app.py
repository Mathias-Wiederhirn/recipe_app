import streamlit as st
import math
import streamlit.components.v1 as components
from utils import search_recipes
from generate_pdf import create_shopping_list_pdf

PAGE_SIZE = 12  # 12 recipe cards per page
API_FETCH_LIMIT = 600  # how many to fetch per search; adjust if you want more pages

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
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# ======================================================
# Instant-react Filters (OUTSIDE the form to avoid delay)
# ======================================================
st.markdown("### 🧪 Filters")

gluten_free = st.toggle("🌾 Gluten-Free Only", key="gluten_toggle", value=False)

use_max_calories = st.toggle("⚡ Max Calories Filter", key="maxc_toggle", value=False)
if use_max_calories:
    max_calories = st.slider("Max Calories (kcal)", 100, 1500, 1000, step=50, key="maxc_slider")
else:
    max_calories = None

use_min_protein = st.toggle("💪 Min Protein Filter", key="minp_toggle", value=False)
if use_min_protein:
    min_protein = st.slider("Min Protein (g)", 0, 100, 5, step=5, key="minp_slider")
else:
    min_protein = None

st.markdown("---")

# --------------------------
# Search form (submit action)
# --------------------------
with st.form("search_form"):
    query = st.text_input("🔍 Enter a keyword (e.g., egg, chicken, pasta):", placeholder="egg")

    meal_types = ["🍽️ Any", "🍳 Breakfast", "🥪 Lunch", "🍝 Dinner", "🍪 Snack"]
    meal_type_selection = st.selectbox("🏷️ Select Meal Type", meal_types)
    meal_type_clean = meal_type_selection.split(" ", 1)[-1].lower()
    meal_type = None if "any" in meal_type_clean else meal_type_clean

    # removed: count slider
    submitted = st.form_submit_button("Search")

# --- Handle empty input ---
if submitted and not query.strip():
    st.warning("🔎 Please enter a keyword to search for recipes!")

# --- Handle search ---
elif submitted:
    health = "gluten-free" if gluten_free else None
    # fetch a fixed number and paginate locally
    results = search_recipes(query, meal_type, None, health, API_FETCH_LIMIT)

    filtered = []
    for recipe in results:
        calories = recipe.get("calories", 0)
        protein = recipe.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0)

        passes_cal = (max_calories is None) or (calories <= max_calories)
        passes_prot = (min_protein is None) or (protein >= min_protein)

        if passes_cal and passes_prot:
            filtered.append(recipe)

    if not filtered:
        st.session_state.recipe_results = []  # 🧹 clear old search results
        st.session_state.current_page = 0
        st.info(f"😕 No recipes found for **{query}**. Try a different keyword or adjust filters!")
    else:
        st.session_state.recipe_results = filtered
        st.session_state.current_page = 0  # reset to first page on new search

# --- Display results with pagination ---
if st.session_state.recipe_results:
    total = len(st.session_state.recipe_results)
    total_pages = max(1, math.ceil(total / PAGE_SIZE))
    current_page = max(0, min(st.session_state.current_page, total_pages - 1))

    start_idx = current_page * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total)
    page_items = st.session_state.recipe_results[start_idx:end_idx]

    st.subheader(f"🍲 Recipes (Page {current_page + 1} of {total_pages})")

    cols_per_row = 3  # 3 x 4 = 12 cards per page
    rows = math.ceil(len(page_items) / cols_per_row)

    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            idx = row * cols_per_row + col_idx
            if idx >= len(page_items):
                break

            recipe = page_items[idx]
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
                        <h4 style="color:#2E86C1; margin-top:0;">{title}</h4>
                        <img src="{image_url}" style="width:100%; border-radius:10px; margin-bottom:1em;" />
                        <p style="font-size: 0.9em; margin: 4px 0;"><strong>Calories:</strong> {calories} kcal</p>
                        <p style="font-size: 0.9em; margin: 4px 0;"><strong>Protein:</strong> {protein:.1f} g</p>
                        <a href="{url}" target="_blank" style="
                            display: inline-block;
                            padding: 8px 16px;
                            background: linear-gradient(135deg, #2980b9, #3498db);
                            color: white;
                            border-radius: 8px;
                            text-decoration: none;
                            font-size: 0.9em;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                            transition: background 0.3s ease, transform 0.2s ease;
                        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            View Full Recipe
                        </a>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("➕ Add to Shopping List", key=f"add_{start_idx+idx}"):
                    st.session_state.shopping_list.append((title, ingredients))
                    st.success(f"✅ Ingredients from '{title}' added! [🛒 Go to Shopping List](#shopping-list)")

    # --- Pagination controls ---
    nav_cols = st.columns([1, 2, 1])
    with nav_cols[0]:
        if st.button("◀ Previous", disabled=(current_page == 0), key="prev_page"):
            st.session_state.current_page = current_page - 1
            st.rerun()
    with nav_cols[1]:
        st.markdown(
            f"<div style='text-align:center; font-weight:600;'>Page {current_page + 1} / {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with nav_cols[2]:
        if st.button("Next ▶", disabled=(current_page >= total_pages - 1), key="next_page"):
            st.session_state.current_page = current_page + 1
            st.rerun()

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

<button onclick="topFunction()" id="scrollTopBtn">⬆️</button>

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

<button onclick="topFunction()" id="scrollTopBtn">⬆️</button>

<script>
const scrollBtn = document.getElementById("scrollTopBtn");
window.onscroll = function() {
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        scrollBtn.style.display = "block";
    } else {
        scrollBtn.style.display = "none";
    }
};
function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
</script>
""", height=0)
