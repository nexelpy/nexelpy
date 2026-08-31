from .nextyleBuilder import Nextyle 


with Nextyle(__file__,layer_order=("reset", "base", "components", "utilities"),costom_size="@media(min-width: 2400x)") as y:
    # y instance need import to anoter module or pass to (View(nextyles=y),Plugin(nextyles=y)) for generate else isnt generate

    y.import_file( y.url("./static/fonts.css") )

    y.select(".btn").background_color("red").color("white").padding("20px")\
        .hover().background_color("yellow").color("black").padding("25px")\
        .active().color("green").checked().color("pink")

    y.select("div").color("black",sm="red",md="blue",lg="green",xl="pink",ul="gray")

    with y.layer("base"):
        y.select("body").background_color("black").color("white").background_image( y.url("./static/page-bg.png") )

    with y.scoping("data-scope-myscop") as scop:
        scop.color("black",sm="red",md="blue",lg="green",xl="pink",ul="gray")
        y.select(".btn").background_color("red").color("white").padding("20px")\
                .hover().background_color("yellow").color("black").padding("25px")\
                .active().color("green").checked().color("pink")

    with y.keyframes("fade-in"):
        y.step("0%").background_color("red").color("white").padding("10px")
        y.step("25%").background_color("orange").color("gray").padding("20px")
        y.step("50%").background_color("yellow").color("black").padding("30px")
        y.step("75%").background_color("orange").color("gray").padding("20px")
        y.step("100%").background_color("red").color("white").padding("10px")

    y.select(".card").animation_name("fade-in").animation_duration("3s").animation_timing_function("ease-in-out")


    with y.scoping():
        with y.keyframes("fade-in") as fade_in:
                y.step("0%").background_color("red").color("white").padding("10px",sm="5px")
                y.step("25%").background_color("orange").color("gray").padding("20px",sm="15px")
                y.step("50%").background_color("yellow").color("black").padding("30px",sm="20px")
                y.step("75%").background_color("orange").color("gray").padding("20px",sm="15px")
                y.step("100%").background_color("red").color("white").padding("10px",sm="5px")
        y.select(".card").animation_name(fade_in).animation_duration("3s").animation_timing_function("ease-in-out")


    with y.scoping("[data-scoping='my-scop']"):
         y.select(".manuel-scop").background_color("black").color("white").background_image( y.url("./static/page-bg.png") )