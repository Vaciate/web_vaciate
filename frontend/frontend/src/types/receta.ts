export interface Receta {
  id: number;
  titulo: string;
  ingredientes: string[] | any; // JSONB a la base de dades
  instrucciones: string;
  creado_el: string;
  es_ia: boolean; // Basat en el teu model de FastAPI 
  es_publica: boolean; // Definit al teu SQL
}