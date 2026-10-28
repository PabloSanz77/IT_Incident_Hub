import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, CheckCircle2, ClipboardList, Search, Server, ShieldCheck } from 'lucide-react'

type Status = 'NUEVO' | 'ASIGNADO' | 'EN_PROCESO' | 'RESUELTO' | 'CERRADO'
type Priority = 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA'
type Incident = {
  id: number; title: string; description: string; category: string; priority: Priority;
  reporter: string; technician: string | null; status: Status; created_at: string
}
type Dashboard = { total: number; open: number; closed: number; critical: number }

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const statusLabels: Record<Status, string> = {
  NUEVO: 'Nuevo', ASIGNADO: 'Asignado', EN_PROCESO: 'En proceso', RESUELTO: 'Resuelto', CERRADO: 'Cerrado'
}

export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [activeSection, setActiveSection] = useState<'incidents' | 'dashboard' | 'services' | 'quality'>('incidents')
  const [dashboard, setDashboard] = useState<Dashboard>({ total: 0, open: 0, closed: 0, critical: 0 })
  const [search, setSearch] = useState('')
  const [statusFilter] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', category: 'Hardware', priority: 'MEDIA' as Priority, reporter: '' })

  async function load() {
    setLoading(true); setError('')
    try {
      const [incRes, dashRes] = await Promise.all([
        fetch(`${API}/incidents`), fetch(`${API}/dashboard`)
      ])
      if (!incRes.ok || !dashRes.ok) throw new Error('La API respondió con un error.')
      setIncidents(await incRes.json())
      setDashboard(await dashRes.json())
    } catch {
      setError('No se pudo conectar con la API. Verifica que Docker esté iniciado y que el backend esté disponible en el puerto 8000.')
    } finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [])

  const visible = useMemo(() => incidents.filter(i =>
    `${i.title} ${i.category} ${i.reporter} ${i.technician ?? ''}`.toLowerCase().includes(search.toLowerCase())
    && (!statusFilter || i.status === statusFilter)
  ), [incidents, search, statusFilter])

  async function createIncident(e: React.FormEvent) {
    e.preventDefault(); setError('')
    try {
      const response = await fetch(`${API}/incidents`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form)
      })
      if (!response.ok) throw new Error('No se pudo guardar el incidente.')
      setForm({ title: '', description: '', category: 'Hardware', priority: 'MEDIA', reporter: '' })
      setShowForm(false); await load()
    } catch (err) { setError(err instanceof Error ? err.message : 'Error al crear incidente.') }
  }

  async function changeStatus(item: Incident, status: Status) {
    try {
      const response = await fetch(`${API}/incidents/${item.id}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status })
      })
      if (!response.ok) throw new Error()
      await load()
    } catch { setError('No se pudo actualizar el estado del incidente.') }
  }

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><Activity size={22} /></span><div><strong>Incident Hub</strong><small>IT OPERATIONS</small></div></div>
      <div className="nav-label">ESPACIO DE TRABAJO</div>
      <div className="nav-item active"><ClipboardList size={18} /> Incidentes <span className="nav-count">{incidents.length}</span></div>
      <div className="nav-item"><Activity size={18} /> Dashboard</div>
      <div
        className={`nav-item ${activeSection === 'services' ? 'active' : ''}`}
        onClick={() => setActiveSection('services')}
      >
        <Server size={18} /> Servicios
      </div>
      <div
        className={`nav-item ${activeSection === 'quality' ? 'active' : ''}`}
        onClick={() => setActiveSection('quality')}
      >
        <ShieldCheck size={18} /> Calidad y operaciones
      </div>
      <div className="sidebar-bottom"><span className="online-dot" /> API de incidentes <small>Conectividad verificada al cargar</small></div>
    </aside>
    <section className="main-content">
  {activeSection === 'services' ? (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Servicios</h2>
          <p>Información de los servicios de TI.</p>
        </div>
      </div>
      <p>Administración y seguimiento de los servicios tecnológicos.</p>
    </section>
  ) : activeSection === 'quality' ? (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Calidad y operaciones</h2>
          <p>Estado de las pruebas y operaciones del sistema.</p>
        </div>
      </div>
      <p>Consulta las operaciones y la calidad del sistema IT Incident Hub.</p>
    </section>
  ) : (
    <>
      <header className="topbar">
        <div>
          <span className="eyebrow">CENTRO DE OPERACIONES / SOPORTE</span>
          <h1>Gestión de incidentes TI</h1>
        </div>
      </header>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <section className="metrics">
        <article className="metric-card">
          <div className="metric-heading">
            Total de incidentes <ClipboardList size={18} />
          </div>
          <strong>{dashboard.total}</strong>
        </article>

        <article className="metric-card">
          <div className="metric-heading">
            Abiertos <Activity size={18} />
          </div>
          <strong>{dashboard.open}</strong>
        </article>

        <article className="metric-card">
          <div className="metric-heading">
            Críticos <AlertTriangle size={18} />
          </div>
          <strong>{dashboard.critical}</strong>
        </article>

        <article className="metric-card">
          <div className="metric-heading">
            Cerrados <CheckCircle2 size={18} />
          </div>
          <strong>{dashboard.closed}</strong>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Incidentes recientes</h2>
            <p>Consulta los registros y actualiza su estado.</p>
          </div>
        </div>

        {showForm && (
          <form className="incident-form" onSubmit={createIncident}>
            <label>
              Título
              <input
                required
                minLength={3}
                value={form.title}
                onChange={(e) =>
                  setForm({ ...form, title: e.target.value })
                }
              />
            </label>

            <label>
              Reportado por
              <input
                required
                minLength={2}
                value={form.reporter}
                onChange={(e) =>
                  setForm({ ...form, reporter: e.target.value })
                }
              />
            </label>

            <label>
              Descripción
              <textarea
                required
                minLength={3}
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </label>

            <div className="form-row">
              <label>
                Categoría
                <select
                  value={form.category}
                  onChange={(e) =>
                    setForm({ ...form, category: e.target.value })
                  }
                >
                  <option value="Hardware">Hardware</option>
                  <option value="Software">Software</option>
                  <option value="Red">Red</option>
                  <option value="Accesos">Accesos</option>
                </select>
              </label>

              <label>
                Prioridad
                <select
                  value={form.priority}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      priority: e.target.value as Priority,
                    })
                  }
                >
                  <option value="BAJA">Baja</option>
                  <option value="MEDIA">Media</option>
                  <option value="ALTA">Alta</option>
                  <option value="CRITICA">Crítica</option>
                </select>
              </label>
            </div>

            <button className="button primary" type="submit">
              Guardar incidente
            </button>
          </form>
        )}

        <div className="toolbar">
          <label className="search-box">
            <Search size={17} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar incidentes..."
            />
          </label>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Incidente</th>
                <th>Categoría</th>
                <th>Prioridad</th>
                <th>Técnico</th>
                <th>Estado</th>
              </tr>
            </thead>

            <tbody>
              {visible.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>
                      INC-{String(item.id).padStart(4, '0')}
                    </strong>
                    <br />
                    {item.title}
                  </td>
                  <td>{item.category}</td>
                  <td>{item.priority}</td>
                  <td>{item.technician ?? 'Sin asignar'}</td>
                  <td>
                    <select
                      value={item.status}
                      onChange={(e) =>
                        changeStatus(item, e.target.value as Status)
                      }
                    >
                      {Object.entries(statusLabels).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}

              {visible.length === 0 && (
                <tr>
                  <td colSpan={5} className="empty">
                    {loading
                      ? 'Cargando incidentes...'
                      : 'No hay incidentes para mostrar.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="table-footer">
          Mostrando {visible.length} de {incidents.length} incidentes
        </div>
      </section>
    </>
  )}
</section>
</main>
;
}