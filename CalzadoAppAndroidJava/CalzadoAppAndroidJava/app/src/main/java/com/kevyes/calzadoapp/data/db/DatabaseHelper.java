package com.kevyes.calzadoapp.data.db;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import com.kevyes.calzadoapp.data.model.CartItem;
import com.kevyes.calzadoapp.data.model.Employee;
import com.kevyes.calzadoapp.data.model.Inventory;
import com.kevyes.calzadoapp.data.model.Shoe;
import com.kevyes.calzadoapp.data.model.TemporaryLoan;

import java.util.ArrayList;
import java.util.List;

public class DatabaseHelper extends SQLiteOpenHelper {
    private static final String DB_NAME = "calzado.db";
    private static final int DB_VERSION = 1;

    public DatabaseHelper(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE employee (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "document TEXT UNIQUE NOT NULL," +
                "name TEXT NOT NULL," +
                "role TEXT NOT NULL)");
        db.execSQL("CREATE TABLE shoe (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "reference TEXT UNIQUE NOT NULL," +
                "brand TEXT NOT NULL," +
                "size INTEGER NOT NULL," +
                "color TEXT NOT NULL," +
                "model TEXT NOT NULL," +
                "price REAL NOT NULL)");
        db.execSQL("CREATE TABLE inventory (" +
                "shoe_id INTEGER PRIMARY KEY," +
                "stock_available INTEGER NOT NULL CHECK(stock_available >= 0)," +
                "stock_test INTEGER NOT NULL CHECK(stock_test >= 0)," +
                "FOREIGN KEY(shoe_id) REFERENCES shoe(id))");
        db.execSQL("CREATE TABLE temporary_loan (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "employee_id INTEGER NOT NULL," +
                "shoe_id INTEGER NOT NULL," +
                "date_exit INTEGER NOT NULL," +
                "date_return INTEGER," +
                "quantity INTEGER NOT NULL CHECK(quantity > 0)," +
                "state TEXT NOT NULL," +
                "FOREIGN KEY(employee_id) REFERENCES employee(id)," +
                "FOREIGN KEY(shoe_id) REFERENCES shoe(id))");
        db.execSQL("CREATE TABLE sale (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "date_time INTEGER NOT NULL," +
                "channel TEXT NOT NULL," +
                "total REAL NOT NULL)");
        db.execSQL("CREATE TABLE sale_detail (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "sale_id INTEGER NOT NULL," +
                "shoe_id INTEGER NOT NULL," +
                "quantity INTEGER NOT NULL," +
                "subtotal REAL NOT NULL," +
                "FOREIGN KEY(sale_id) REFERENCES sale(id)," +
                "FOREIGN KEY(shoe_id) REFERENCES shoe(id))");

        seedEmployees(db);
        seedShoes(db);
    }

    private void seedEmployees(SQLiteDatabase db) {
        insertEmployee(db, "1001", "Vendedor Demo", "EMPLEADO_POS");
        insertEmployee(db, "2001", "Cliente Demo", "CLIENTE_VIRTUAL");
        insertEmployee(db, "3001", "Administrador Demo", "ADMINISTRADOR");
    }

    private void insertEmployee(SQLiteDatabase db, String document, String name, String role) {
        ContentValues values = new ContentValues();
        values.put("document", document);
        values.put("name", name);
        values.put("role", role);
        db.insertOrThrow("employee", null, values);
    }

    private void seedShoes(SQLiteDatabase db) {
        addShoe(db, "REF-001", "Nike", 40, "Negro", "Air Max", 350000, 8);
        addShoe(db, "REF-002", "Adidas", 41, "Blanco", "Run Falcon", 280000, 6);
        addShoe(db, "REF-003", "Puma", 42, "Rojo", "RS-X", 410000, 5);
        addShoe(db, "REF-004", "Reebok", 39, "Azul", "Energen", 240000, 4);
        addShoe(db, "REF-005", "Nike", 42, "Blanco", "Court Vision", 300000, 7);
    }

    private void addShoe(SQLiteDatabase db, String reference, String brand, int size, String color,
                         String model, double price, int stock) {
        ContentValues shoe = new ContentValues();
        shoe.put("reference", reference);
        shoe.put("brand", brand);
        shoe.put("size", size);
        shoe.put("color", color);
        shoe.put("model", model);
        shoe.put("price", price);
        long id = db.insertOrThrow("shoe", null, shoe);

        ContentValues inventory = new ContentValues();
        inventory.put("shoe_id", id);
        inventory.put("stock_available", stock);
        inventory.put("stock_test", 0);
        db.insertOrThrow("inventory", null, inventory);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS sale_detail");
        db.execSQL("DROP TABLE IF EXISTS sale");
        db.execSQL("DROP TABLE IF EXISTS temporary_loan");
        db.execSQL("DROP TABLE IF EXISTS inventory");
        db.execSQL("DROP TABLE IF EXISTS shoe");
        db.execSQL("DROP TABLE IF EXISTS employee");
        onCreate(db);
    }

    public Employee findEmployeeByDocument(String document) {
        SQLiteDatabase db = getReadableDatabase();
        try (Cursor c = db.query("employee", null, "document = ?", new String[]{document}, null, null, null)) {
            if (c.moveToFirst()) {
                return new Employee(c.getLong(c.getColumnIndexOrThrow("id")),
                        c.getString(c.getColumnIndexOrThrow("document")),
                        c.getString(c.getColumnIndexOrThrow("name")),
                        c.getString(c.getColumnIndexOrThrow("role")));
            }
        }
        return null;
    }

    public List<Shoe> getAvailableShoes(String sizeText, String colorText) {
        List<Shoe> result = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();
        List<String> clauses = new ArrayList<>();
        List<String> args = new ArrayList<>();
        clauses.add("i.shoe_id = s.id");
        clauses.add("i.stock_available > 0");
        if (!"TODAS".equals(sizeText)) {
            clauses.add("s.size = ?");
            args.add(sizeText);
        }
        if (!"TODOS".equals(colorText)) {
            clauses.add("s.color = ?");
            args.add(colorText);
        }
        String sql = "SELECT s.* FROM shoe s, inventory i WHERE " + String.join(" AND ", clauses) + " ORDER BY s.brand, s.model";
        try (Cursor c = db.rawQuery(sql, args.toArray(new String[0]))) {
            while (c.moveToNext()) {
                result.add(mapShoe(c));
            }
        }
        return result;
    }

    public List<Shoe> getAllShoes() {
        List<Shoe> result = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query("shoe", null, null, null, null, null, "brand, model")) {
            while (c.moveToNext()) result.add(mapShoe(c));
        }
        return result;
    }

    public Inventory getInventory(long shoeId) {
        try (Cursor c = getReadableDatabase().query("inventory", null, "shoe_id = ?",
                new String[]{String.valueOf(shoeId)}, null, null, null)) {
            if (c.moveToFirst()) {
                return new Inventory(shoeId,
                        c.getInt(c.getColumnIndexOrThrow("stock_available")),
                        c.getInt(c.getColumnIndexOrThrow("stock_test")));
            }
        }
        return null;
    }

    public Shoe getShoe(long shoeId) {
        try (Cursor c = getReadableDatabase().query("shoe", null, "id = ?",
                new String[]{String.valueOf(shoeId)}, null, null, null)) {
            if (c.moveToFirst()) return mapShoe(c);
        }
        return null;
    }

    private Shoe mapShoe(Cursor c) {
        return new Shoe(c.getLong(c.getColumnIndexOrThrow("id")),
                c.getString(c.getColumnIndexOrThrow("reference")),
                c.getString(c.getColumnIndexOrThrow("brand")),
                c.getInt(c.getColumnIndexOrThrow("size")),
                c.getString(c.getColumnIndexOrThrow("color")),
                c.getString(c.getColumnIndexOrThrow("model")),
                c.getDouble(c.getColumnIndexOrThrow("price")));
    }

    public long registerTemporaryLoan(long employeeId, long shoeId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("La cantidad debe ser mayor que cero.");
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            Inventory inventory = getInventory(shoeId);
            if (inventory == null) throw new IllegalArgumentException("El inventario no existe.");
            if (inventory.getStockAvailable() < quantity) {
                throw new IllegalStateException("No hay stock disponible suficiente.");
            }

            updateInventoryInternal(db, shoeId,
                    inventory.getStockAvailable() - quantity,
                    inventory.getStockInTest() + quantity);

            ContentValues values = new ContentValues();
            values.put("employee_id", employeeId);
            values.put("shoe_id", shoeId);
            values.put("date_exit", System.currentTimeMillis());
            values.put("quantity", quantity);
            values.put("state", TemporaryLoan.RESERVED);
            long loanId = db.insertOrThrow("temporary_loan", null, values);
            db.setTransactionSuccessful();
            return loanId;
        } finally {
            db.endTransaction();
        }
    }

    public void returnTemporaryLoan(long loanId) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            TemporaryLoan loan = getLoan(loanId);
            if (loan == null || !TemporaryLoan.RESERVED.equals(loan.getState())) {
                throw new IllegalStateException("El préstamo ya fue liquidado o no existe.");
            }
            Inventory inventory = getInventory(loan.getShoeId());
            if (inventory == null || inventory.getStockInTest() < loan.getQuantity()) {
                throw new IllegalStateException("El stock en prueba no es consistente.");
            }
            updateInventoryInternal(db, loan.getShoeId(),
                    inventory.getStockAvailable() + loan.getQuantity(),
                    inventory.getStockInTest() - loan.getQuantity());
            ContentValues values = new ContentValues();
            values.put("date_return", System.currentTimeMillis());
            values.put("state", TemporaryLoan.RETURNED);
            db.update("temporary_loan", values, "id = ?", new String[]{String.valueOf(loanId)});
            db.setTransactionSuccessful();
        } finally {
            db.endTransaction();
        }
    }

    public long sellTemporaryLoan(long loanId) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            TemporaryLoan loan = getLoan(loanId);
            if (loan == null || !TemporaryLoan.RESERVED.equals(loan.getState())) {
                throw new IllegalStateException("El préstamo ya fue liquidado o no existe.");
            }
            Inventory inventory = getInventory(loan.getShoeId());
            Shoe shoe = getShoe(loan.getShoeId());
            if (inventory == null || shoe == null || inventory.getStockInTest() < loan.getQuantity()) {
                throw new IllegalStateException("El stock en prueba no es consistente.");
            }

            double total = shoe.getPrice() * loan.getQuantity();
            ContentValues sale = new ContentValues();
            sale.put("date_time", System.currentTimeMillis());
            sale.put("channel", "PRESENCIAL");
            sale.put("total", total);
            long saleId = db.insertOrThrow("sale", null, sale);

            ContentValues detail = new ContentValues();
            detail.put("sale_id", saleId);
            detail.put("shoe_id", loan.getShoeId());
            detail.put("quantity", loan.getQuantity());
            detail.put("subtotal", total);
            db.insertOrThrow("sale_detail", null, detail);

            updateInventoryInternal(db, loan.getShoeId(),
                    inventory.getStockAvailable(),
                    inventory.getStockInTest() - loan.getQuantity());

            ContentValues loanValues = new ContentValues();
            loanValues.put("date_return", System.currentTimeMillis());
            loanValues.put("state", TemporaryLoan.SOLD);
            db.update("temporary_loan", loanValues, "id = ?", new String[]{String.valueOf(loanId)});
            db.setTransactionSuccessful();
            return saleId;
        } finally {
            db.endTransaction();
        }
    }

    private void updateInventoryInternal(SQLiteDatabase db, long shoeId, int available, int test) {
        ContentValues values = new ContentValues();
        values.put("stock_available", available);
        values.put("stock_test", test);
        int updated = db.update("inventory", values, "shoe_id = ?", new String[]{String.valueOf(shoeId)});
        if (updated != 1) throw new IllegalStateException("No se pudo actualizar el inventario.");
    }

    public List<TemporaryLoan> getActiveLoans(long employeeId) {
        List<TemporaryLoan> result = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query("temporary_loan", null,
                "employee_id = ? AND state = ?",
                new String[]{String.valueOf(employeeId), TemporaryLoan.RESERVED},
                null, null, "date_exit DESC")) {
            while (c.moveToNext()) result.add(mapLoan(c));
        }
        return result;
    }

    public TemporaryLoan getLoan(long loanId) {
        try (Cursor c = getReadableDatabase().query("temporary_loan", null, "id = ?",
                new String[]{String.valueOf(loanId)}, null, null, null)) {
            if (c.moveToFirst()) return mapLoan(c);
        }
        return null;
    }

    private TemporaryLoan mapLoan(Cursor c) {
        return new TemporaryLoan(c.getLong(c.getColumnIndexOrThrow("id")),
                c.getLong(c.getColumnIndexOrThrow("employee_id")),
                c.getLong(c.getColumnIndexOrThrow("shoe_id")),
                c.getLong(c.getColumnIndexOrThrow("date_exit")),
                c.isNull(c.getColumnIndexOrThrow("date_return")) ? 0 : c.getLong(c.getColumnIndexOrThrow("date_return")),
                c.getInt(c.getColumnIndexOrThrow("quantity")),
                c.getString(c.getColumnIndexOrThrow("state")));
    }

    public double getOnlineCartTotal(List<CartItem> cartItems) {
        double total = 0;
        for (CartItem item : cartItems) total += item.getSubtotal();
        return total;
    }

    public long buyOnline(List<CartItem> cartItems) {
        if (cartItems == null || cartItems.isEmpty()) throw new IllegalArgumentException("El carrito está vacío.");
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            double total = 0;
            for (CartItem item : cartItems) {
                Inventory inventory = getInventory(item.getShoe().getIdZapato());
                if (inventory == null || inventory.getStockAvailable() < item.getQuantity()) {
                    throw new IllegalStateException("Stock insuficiente para " + item.getShoe());
                }
                total += item.getSubtotal();
            }

            ContentValues sale = new ContentValues();
            sale.put("date_time", System.currentTimeMillis());
            sale.put("channel", "VIRTUAL");
            sale.put("total", total);
            long saleId = db.insertOrThrow("sale", null, sale);

            for (CartItem item : cartItems) {
                Inventory inventory = getInventory(item.getShoe().getIdZapato());
                updateInventoryInternal(db, item.getShoe().getIdZapato(),
                        inventory.getStockAvailable() - item.getQuantity(),
                        inventory.getStockInTest());

                ContentValues detail = new ContentValues();
                detail.put("sale_id", saleId);
                detail.put("shoe_id", item.getShoe().getIdZapato());
                detail.put("quantity", item.getQuantity());
                detail.put("subtotal", item.getSubtotal());
                db.insertOrThrow("sale_detail", null, detail);
            }
            db.setTransactionSuccessful();
            return saleId;
        } finally {
            db.endTransaction();
        }
    }

    public String buildAuditCsv(String employeeDocument, long fromMillis, long toMillis) {
        StringBuilder csv = new StringBuilder();
        csv.append("Prestamo;Empleado;Documento;Zapato;Cantidad;Salida;Retorno;Estado\n");
        String sql = "SELECT t.id, e.name, e.document, s.brand || ' ' || s.model AS shoe_name, " +
                "t.quantity, t.date_exit, t.date_return, t.state " +
                "FROM temporary_loan t " +
                "JOIN employee e ON e.id = t.employee_id " +
                "JOIN shoe s ON s.id = t.shoe_id " +
                "WHERE t.date_exit BETWEEN ? AND ? ";
        List<String> args = new ArrayList<>();
        args.add(String.valueOf(fromMillis));
        args.add(String.valueOf(toMillis));
        if (employeeDocument != null && !employeeDocument.trim().isEmpty()) {
            sql += "AND e.document = ? ";
            args.add(employeeDocument.trim());
        }
        sql += "ORDER BY t.date_exit DESC";

        try (Cursor c = getReadableDatabase().rawQuery(sql, args.toArray(new String[0]))) {
            while (c.moveToNext()) {
                csv.append(c.getLong(0)).append(';')
                        .append(c.getString(1)).append(';')
                        .append(c.getString(2)).append(';')
                        .append(c.getString(3)).append(';')
                        .append(c.getInt(4)).append(';')
                        .append(c.getLong(5)).append(';')
                        .append(c.isNull(6) ? "" : c.getLong(6)).append(';')
                        .append(c.getString(7)).append('\n');
            }
        }
        return csv.toString();
    }

    public List<String> getAuditLines(String employeeDocument, long fromMillis, long toMillis) {
        List<String> result = new ArrayList<>();
        String sql = "SELECT e.name, e.document, s.brand, s.model, t.quantity, t.date_exit, t.date_return, t.state " +
                "FROM temporary_loan t JOIN employee e ON e.id=t.employee_id JOIN shoe s ON s.id=t.shoe_id " +
                "WHERE t.date_exit BETWEEN ? AND ? ";
        List<String> args = new ArrayList<>();
        args.add(String.valueOf(fromMillis));
        args.add(String.valueOf(toMillis));
        if (employeeDocument != null && !employeeDocument.trim().isEmpty()) {
            sql += "AND e.document = ? ";
            args.add(employeeDocument.trim());
        }
        sql += "ORDER BY t.date_exit DESC";
        try (Cursor c = getReadableDatabase().rawQuery(sql, args.toArray(new String[0]))) {
            while (c.moveToNext()) {
                result.add(c.getString(0) + " | Doc: " + c.getString(1) +
                        " | " + c.getString(2) + " " + c.getString(3) +
                        " | Cant: " + c.getInt(4) +
                        " | Salida: " + c.getLong(5) +
                        " | Retorno: " + (c.isNull(6) ? "-" : c.getLong(6)) +
                        " | Estado: " + c.getString(7));
            }
        }
        return result;
    }
}
