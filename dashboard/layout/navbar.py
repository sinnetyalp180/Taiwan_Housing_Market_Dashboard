import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More", 
            align_end=True
        )
    ],
    # brand="CG servo loading analysis",
    brand="Taiwan Housing Market Analytics",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
    class_name='mb-3'
)
