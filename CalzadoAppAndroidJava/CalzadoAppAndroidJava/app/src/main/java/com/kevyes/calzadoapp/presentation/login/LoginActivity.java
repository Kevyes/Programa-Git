package com.kevyes.calzadoapp.presentation.login;

import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.Toast;

import android.app.Activity;

import com.kevyes.calzadoapp.data.db.DatabaseHelper;
import com.kevyes.calzadoapp.data.model.Employee;
import com.kevyes.calzadoapp.presentation.admin.AdminActivity;
import com.kevyes.calzadoapp.presentation.catalog.CatalogActivity;
import com.kevyes.calzadoapp.presentation.common.Ui;
import com.kevyes.calzadoapp.presentation.pos.PosActivity;
import com.kevyes.calzadoapp.security.AuthService;
import com.kevyes.calzadoapp.security.SessionManager;

public class LoginActivity extends Activity {
    private DatabaseHelper database;
    private EditText username;
    private EditText password;
    private Spinner role;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        database = new DatabaseHelper(this);
        SessionManager session = new SessionManager(this);
        if (session.isLoggedIn()) {
            openRole(session.getRole());
            return;
        }

        LinearLayout root = Ui.page(this);
        root.addView(Ui.title(this, "Calzado App\nInicio / Login"));

        username = new EditText(this);
        username.setHint("Usuario: empleado / cliente / admin");
        root.addView(username);

        password = new EditText(this);
        password.setHint("Contraseña de demostración: 1234");
        password.setInputType(0x00000081);
        root.addView(password);

        root.addView(Ui.label(this, "Rol"));
        role = new Spinner(this);
        String[] roles = {"EMPLEADO_POS", "CLIENTE_VIRTUAL", "ADMINISTRADOR"};
        role.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, roles));
        root.addView(role);

        android.widget.Button login = Ui.button(this, "Ingresar");
        root.addView(login);
        root.addView(Ui.label(this,
                "Demo local: la app usa SQLite para pruebas. En producción el JWT y las credenciales deben ser validados por el backend."));

        login.setOnClickListener(v -> authenticate());
        setContentView(root);
    }

    private void authenticate() {
        String selectedRole = String.valueOf(role.getSelectedItem());
        Employee employee = new AuthService(database).authenticate(
                username.getText().toString().trim(),
                password.getText().toString(),
                selectedRole);
        if (employee == null) {
            Toast.makeText(this, "Credenciales o rol incorrectos.", Toast.LENGTH_SHORT).show();
            return;
        }

        new SessionManager(this).login(employee.getIdEmpleado(), employee.getName(), employee.getRole());
        openRole(employee.getRole());
    }

    private void openRole(String roleName) {
        Intent intent;
        switch (roleName) {
            case "EMPLEADO_POS": intent = new Intent(this, PosActivity.class); break;
            case "CLIENTE_VIRTUAL": intent = new Intent(this, CatalogActivity.class); break;
            case "ADMINISTRADOR": intent = new Intent(this, AdminActivity.class); break;
            default:
                new SessionManager(this).logout();
                return;
        }
        startActivity(intent);
        finish();
    }
}
