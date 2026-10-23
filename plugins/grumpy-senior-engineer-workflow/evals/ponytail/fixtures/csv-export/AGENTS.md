Python standard library only. Records contain id, tenant, date, description, cents.
Dates are valid ISO YYYY-MM-DD strings; ids are strings and cents are integers.
Public CLI: python3 cli.py FILE --tenant T --start DATE --end DATE.
Architecture settled: query.select owns selection/order; csv_output.render owns CSV.
