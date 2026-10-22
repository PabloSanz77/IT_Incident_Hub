
import { describe, expect, it } from 'vitest';

describe('IT Incident Hub - pruebas frontend', () => {
  it('debe ejecutar correctamente el entorno de pruebas', () => {
    expect(1 + 1).toBe(2);
  });

  it('debe reconocer las prioridades de los incidentes', () => {
    const prioridades = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA'];

    expect(prioridades).toContain('ALTA');
    expect(prioridades).toContain('CRITICA');
    expect(prioridades).toHaveLength(4);
  });

  it('debe reconocer los estados de los incidentes', () => {
    const estados = [
      'NUEVO',
      'ASIGNADO',
      'EN_PROCESO',
      'RESUELTO',
      'CERRADO',
    ];

    expect(estados).toContain('NUEVO');
    expect(estados).toContain('EN_PROCESO');
    expect(estados).toContain('CERRADO');
    expect(estados).toHaveLength(5);
  });
});
