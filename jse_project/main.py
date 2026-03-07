html_output = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JSE Market Cap App</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            margin: 40px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
        }}
        h2 {{
            color: #34495e;
            text-align: center;
        }}
        h3 {{
            color: #16a085;
            text-align: center;
        }}
        table {{
            margin: 20px auto;
            border-collapse: collapse;
            width: 60%;
            background-color: #fff;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ccc;
            text-align: center;
        }}
        th {{
            background-color: #2c3e50;
            color: #fff;
        }}
        p {{
            text-align: center;
            font-size: 0.9em;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>JSE Market Cap App</h1>
    <h2>Naspers (NPN.JO) - Last 5 Years</h2>
    <h3>Latest Price: {latest_price} ZAR</h3>
    <p>Data provided via Yahoo Finance</p>
    {html_table}
</body>
</html>
"""