from .nextyleBuilder import Nextyle


with Nextyle(__file__, layer_order=("reset", "base", "components", "utilities")) as y:
    # --- import external CSS ---
    y.import_css(y.url("./static/fonts.css"))

    # --- simple selectors ---
    y.select(".btn").background_color("red").color("white").padding("20px")\
        .hover().background_color("yellow").color("black").padding("25px")\
        .active().color("green").checked().color("pink")

    y.select("div").color("black", sm="red", md="blue", lg="green", xl="pink", ul="gray")

    # --- layer ---
    with y.layer("base"):
        y.select("body").background_color("black").color("white").background_image(y.url("./static/page-bg.png"))

    # --- scoping with explicit selector ---
    with y.scoping("data-scope-myscop") as scop: 
        scop.color("black", sm="red", md="blue", lg="green", xl="pink", ul="gray")
        y.select(".btn").background_color("red").color("white").padding("20px")\
            .hover().background_color("yellow").color("black").padding("25px")

    # --- keyframes ---
    with y.keyframes("fade-in"):
        y.step("0%").background_color("red").color("white").padding("10px")
        y.step("25%").background_color("orange").color("gray").padding("20px")
        y.step("50%").background_color("yellow").color("black").padding("30px")
        y.step("75%").background_color("orange").color("gray").padding("20px")
        y.step("100%").background_color("red").color("white").padding("10px")

    y.select(".card").animation_name("fade-in").animation_duration("3s").animation_timing_function("ease-in-out")

    # --- scoping auto (data-scoping attribute) --- if empty selector, it will be auto generate with data-scoping attribute and unique token
    with y.scoping():
        with y.keyframes("fade-in") as fade_in:
            y.step("0%").background_color("red").color("white").padding("10px", sm="5px")
            y.step("25%").background_color("orange").color("gray").padding("20px", sm="15px")
            y.step("50%").background_color("yellow").color("black").padding("30px", sm="20px")
            y.step("75%").background_color("orange").color("gray").padding("20px", sm="15px")
            y.step("100%").background_color("red").color("white").padding("10px", sm="5px")
        y.select(".card").animation_name(fade_in).animation_duration("3s")

    # --- manual scoping ---
    with y.scoping("[data-scoping='my-scop']"):
        y.select(".manuel-scop").background_color("black").color("white").background_image(y.url("./static/page-bg.png"))

    # --- media query (standalone) ---
    with y.media("(min-width: 1024px)"):
        y.select(".hero").font_size("3rem")

    # --- supports (feature query) ---
    with y.supports("(display: grid)"):
        y.select(".grid").display("grid").gap("1rem")

    # --- container query ---
    with y.container("(min-width: 400px)", name="card-container"):
        y.select(".card").padding("20px")

    # --- font-face ---
    with y.font_face("MyFont"):
        y.src(y.url("./static/fonts/MyFont.woff2"), format="woff2")
        y.font_weight("400")
        y.font_style("normal")

    # --- property (CSS Houdini custom property) ---
    with y.property("--my-color"):
        y.syntax("<color>")
        y.inherits(False)
        y.initial_value("red")

    # --- vars (custom properties on :root) ---
    with y.vars(":root"):
        y.add_var(primary="#ff0000", secondary="#00ff00")

    # --- scope (CSS @scope) ---
    with y.scope(".card", to=".card-content"):
        y.select("p").color("gray")

    # --- starting-style ---
    with y.starting_style():
        y.select(".fade-in").opacity("0")
    y.select(".fade-in").transition("opacity 0.3s").opacity("1")

    # --- @page ---
    with y.page():
        y.margin("1cm")
        y.size("A4")

    # --- attr and add_var ---
    y.attr(data_theme="dark").add_var(spacing="8px")

    # --- raw CSS ---
    y.raw_css("""
    body {
        color: red;
    }
    """)

    # --- global raw CSS (outside any context) ---
    y.add_global_raw_css("""
    * {
        box-sizing: border-box;
    }
    """)