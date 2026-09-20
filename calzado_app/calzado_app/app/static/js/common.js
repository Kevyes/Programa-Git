/* Utilidades compartidas por las tres pantallas (tienda, POS, administración). */
const API = "/api";

const Sesion = {
  get token() { return sessionStorage.getItem("token"); },
  get rol() { return sessionStorage.getItem("rol"); },
  get nombre() { return sessionStorage.getItem("nombre"); },
  guardar(d) {
    sessionStorage.setItem("token", d.access_token);
    sessionStorage.setItem("rol", d.rol);
    sessionStorage.setItem("nombre", d.nombre);
  },
  cerrar() { sessionStorage.clear(); location.reload(); },
};

/* Escapa texto antes de insertarlo como HTML (previene XSS). */
function esc(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const dinero = n => new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(n);
const fechaLocal = iso => (iso ? new Date(iso).toLocaleString("es-CO") : "—");

async function api(ruta, { metodo = "GET", cuerpo, crudo = false } = {}) {
  const cabeceras = { "Content-Type": "application/json" };
  if (Sesion.token) cabeceras.Authorization = "Bearer " + Sesion.token;
  const r = await fetch(API + ruta, { method: metodo, headers: cabeceras, body: cuerpo ? JSON.stringify(cuerpo) : undefined });
  if (!r.ok) {
    if (r.status === 401 && Sesion.token) { Sesion.cerrar(); }
    let detalle = "Error " + r.status;
    try {
      const j = await r.json();
      detalle = typeof j.detail === "string" ? j.detail : (j.detail || []).map(e => e.msg).join("; ");
    } catch (_) { /* respuesta sin JSON */ }
    throw new Error(detalle);
  }
  return crudo ? r : r.json();
}

function aviso(elemento, texto, tipo = "error") {
  elemento.textContent = texto;
  elemento.className = "msg " + tipo;
}

/* Dibuja la caja de inicio de sesión. Llama onListo() cuando hay sesión con un rol permitido. */
function montarSesion(contenedor, rolesPermitidos, onListo, permitirRegistro = false) {
  const caja = document.getElementById(contenedor);
  if (Sesion.token && rolesPermitidos.includes(Sesion.rol)) {
    caja.innerHTML = `<span>Hola, <b>${esc(Sesion.nombre)}</b> (${esc(Sesion.rol)}) </span><button class="sec" id="btn-salir">Salir</button>`;
    document.getElementById("btn-salir").onclick = () => Sesion.cerrar();
    onListo();
    return;
  }
  const aviso_rol = Sesion.token ? `<div class="msg error">Tu rol (${esc(Sesion.rol)}) no tiene acceso a esta pantalla.</div>` : "";
  caja.innerHTML = `${aviso_rol}
    <form id="form-login" class="fila">
      <label>Correo<input type="email" id="lg-email" required></label>
      <label>Contraseña<input type="password" id="lg-pass" required></label>
      <button type="submit">Ingresar</button>
      ${permitirRegistro ? '<button type="button" class="sec" id="btn-reg">Crear cuenta</button>' : ""}
      ${Sesion.token ? '<button type="button" class="sec" id="btn-out">Cerrar sesión</button>' : ""}
    </form><div id="lg-msg" class="msg"></div>`;
  const msg = document.getElementById("lg-msg");
  if (Sesion.token) document.getElementById("btn-out").onclick = () => Sesion.cerrar();
  document.getElementById("form-login").onsubmit = async e => {
    e.preventDefault();
    try {
      Sesion.guardar(await api("/auth/login", { metodo: "POST", cuerpo: { email: lgv("lg-email"), password: lgv("lg-pass") } }));
      location.reload();
    } catch (err) { aviso(msg, err.message); }
  };
  if (permitirRegistro) {
    document.getElementById("btn-reg").onclick = async () => {
      const nombre = prompt("Tu nombre completo:");
      if (!nombre) return;
      try {
        await api("/auth/registro", { metodo: "POST", cuerpo: { nombre, email: lgv("lg-email"), password: lgv("lg-pass") } });
        aviso(msg, "Cuenta creada. Ya puedes ingresar.", "ok");
      } catch (err) { aviso(msg, err.message); }
    };
  }
}
const lgv = id => document.getElementById(id).value;
