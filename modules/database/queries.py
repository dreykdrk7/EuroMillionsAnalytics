class Queries:
    """
    SQL queries for database operations.
    """

    # Create tables
    CREATE_RESULTS_TABLE = """
    CREATE TABLE IF NOT EXISTS resultados_sorteos (
        id_sorteo TEXT PRIMARY KEY,
        combinacion TEXT,
        combinacion_json TEXT,
        num1 INTEGER,
        num2 INTEGER,
        num3 INTEGER,
        num4 INTEGER,
        num5 INTEGER,
        estrella1 INTEGER,
        estrella2 INTEGER,
        fecha_sorteo TEXT,
        dia_semana TEXT,
        anyo TEXT,
        numero INTEGER,
        premio_bote TEXT,
        apuestas INTEGER,
        combinacion_acta TEXT,
        premios TEXT,
        escrutinio TEXT,
        num_pares INTEGER,
        num_impares INTEGER,
        num_bajos INTEGER,
        num_altos INTEGER,
        secuencias INTEGER
    );
    """

    CREATE_SIMULATED_TABLE = """
    CREATE TABLE IF NOT EXISTS simulated_draws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        combination TEXT
    );
    """

    # Check if a draw is already registered
    CHECK_DRAW = """
    SELECT 1 FROM resultados_sorteos WHERE id_sorteo = ?;
    """

    # Insert a new draw
    INSERT_DRAW = """
    INSERT INTO resultados_sorteos (
        id_sorteo, combinacion, combinacion_json, num1, num2, num3, num4, num5,
        estrella1, estrella2, fecha_sorteo, dia_semana, anyo, numero,
        premio_bote, apuestas, combinacion_acta, premios, escrutinio
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    # Classify draw
    CLASSIFY_FIGURES = """
    UPDATE resultados_sorteos
    SET num_pares = ?, num_impares = ?
    WHERE id_sorteo = ?;
    """

    CLASSIFY_SEQUENCES = """
    UPDATE resultados_sorteos
    SET secuencias = ?
    WHERE id_sorteo = ?;
    """

    CLASSIFY_RANGES = """
    UPDATE resultados_sorteos
    SET num_bajos = ?, num_altos = ?
    WHERE id_sorteo = ?;
    """
