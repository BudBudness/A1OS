import { api } from "../api/client.js";

export function resource(path) {
  return {
    list: () => api.get(path),
    get: (id) => api.get(`${path}/${id}`),
    create: (data) => api.post(path, data),
    update: (id, data) => api.patch(`${path}/${id}`, data),
    remove: (id) => api.delete(`${path}/${id}`)
  };
}
