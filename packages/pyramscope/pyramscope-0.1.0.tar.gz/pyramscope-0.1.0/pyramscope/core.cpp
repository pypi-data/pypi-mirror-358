#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/functional.h>
#include <pybind11/embed.h>
#include <fstream>
#include <unordered_set>
#include <vector>
#include <algorithm>

namespace py = pybind11;

/**
 * Devuelve el tamaño superficial de un objeto Python en bytes.
 * Internamente llama a sys.getsizeof(obj).
 */
std::size_t get_size(const py::object &obj) {
    static py::object sys = py::module_::import("sys");
    return sys.attr("getsizeof")(obj).cast<std::size_t>();
}


/**
Devuelve la direccion en memoria para ver como esta mapeada
*/
std::uintptr_t get_id(py::object obj) {
    return reinterpret_cast<std::uintptr_t>(obj.ptr());
}

/** Obtener una lista de los nombres de los atributos de un objeto Python */
std::vector<std::string> get_attrs(py::object obj) {
    py::list attrs = py::cast<py::list>(py::module_::import("builtins").attr("dir")(obj));
    std::vector<std::string> result;
    for(auto attr : attrs){
        result.push_back(attr.cast<std::string>());
    }
    return result;
}
/** Obtener la lista de objetos que referencian (tienen como referencia) al objeto dado */
std::vector<py::object> get_refs(py::object obj) {
    // Importamos el módulo gc
    py::module gc = py::module::import("gc");

    // Llamamos a gc.get_referrers(obj)
    py::list refs = gc.attr("get_referrers")(obj);

    // Convertimos la lista a vector para devolver
    std::vector<py::object> result;
    for (auto ref : refs) {
        result.push_back(py::reinterpret_borrow<py::object>(ref));
    }

    return result;
}

/** Obtener todos los objetos a los que el objeto dado hace referencia */
py::list get_referents(py::object obj) {
    py::object gc = py::module_::import("gc");
    py::object referents = gc.attr("get_referents")(obj);
    return referents;
}

/** Detectar aliasing — es decir, identificar qué variables u objetos comparten la misma referencia en memoria.  */

py::list get_aliases(py::object obj){
    py::list aliases;
    py::object gc = py::module_::import("gc");
    py::list all_objects = gc.attr("get_objects")();

    PyObject* target_ptr = obj.ptr();
    for(auto item : all_objects){
        if(item.ptr() == target_ptr) {
            aliases.append(item);
        }
    }

    return aliases;
}


/* ------------------ helper recursivo ------------------ */
std::size_t _deep_size(py::handle obj,std::unordered_set<PyObject*> &seen,const py::object &pysys) {
    PyObject *raw  = obj.ptr();
    if(seen.count(raw)){
        return 0;
    }
    seen.insert(raw);
    std::size_t total  = pysys.attr("getsizeof")(obj).cast<std::size_t>();

    if (PyList_Check(raw) || PyTuple_Check(raw)) {
        for (auto item : obj) total += _deep_size(item, seen, pysys);
    } else if (PyDict_Check(raw)) {
        py::dict d = py::reinterpret_borrow<py::dict>(obj);
        for (auto kv : d)
            total += _deep_size(kv.first, seen, pysys) + _deep_size(kv.second, seen, pysys);
    } else if (PySet_Check(raw)) {
        for (auto item : obj) total += _deep_size(item, seen, pysys);
    } else if (PyObject_HasAttrString(raw, "__dict__")) {
        py::object d = obj.attr("__dict__");
        total += _deep_size(d, seen, pysys);
    }
    return total;
}

std::size_t deep_size(py::object obj) {
    static py::object pysys = py::module_::import("sys");
    std::unordered_set<PyObject*> seen;
    return _deep_size(obj, seen, pysys);
}

/* Identificar y listar los objetos que ocupan más memoria en un conjunto dado, ordenados de mayor a menor tamaño. */
py::list get_top_heavy_objects(py::list objects, std::size_t top_n = 10) {
    py::object pysys = py::module_::import("sys");
    std::vector<std::pair<py::object, std::size_t>> sizes;
    std::unordered_set<PyObject*> visited;


    for (auto obj : objects) {
        std::size_t size = _deep_size(obj, visited, pysys);
        sizes.emplace_back(py::reinterpret_borrow<py::object>(obj), size);  // ✅ conversión + punto y coma
    }

    // Ordenar de mayor a menor tamaño
    std::sort(sizes.begin(), sizes.end(), [](const auto& a, const auto& b) {
        return a.second > b.second;
    });

    py::list result;

    // Devolver los top N objetos con su tamaño
    for (std::size_t i = 0; i < std::min(top_n, sizes.size()); ++i) {
        py::dict entry;
        entry["object"] = sizes[i].first;
        entry["size"] = sizes[i].second;
        result.append(entry);
    }

    return result;
}

/* Calcula la profundidad de anidamiento de una estructura*/

std::size_t _depth(py::handle obj,
                   std::unordered_set<PyObject*> &seen)
{
    PyObject *raw = obj.ptr();

    // Evitar ciclos / alias 
    if (seen.count(raw))
        return 0;
    seen.insert(raw);

    // Si es contenedor (list, tuple, dict, set) computamos hijos
    if (PyList_Check(raw) || PyTuple_Check(raw) || PySet_Check(raw))
    {
        std::size_t max_child = 0;
        for (auto item : obj)
            max_child = std::max(max_child, _depth(item, seen));
        return 1 + max_child;
    }
    else if (PyDict_Check(raw))
    {
        std::size_t max_child = 0;
        py::dict d = py::reinterpret_borrow<py::dict>(obj);
        for (auto kv : d)
        {
            max_child = std::max(max_child, _depth(kv.first,  seen));
            max_child = std::max(max_child, _depth(kv.second, seen));
        }
        return 1 + max_child;
    }
    else if (PyObject_HasAttrString(raw, "__dict__"))
    {
        return 1 + _depth(obj.attr("__dict__"), seen);
    }

    // No es contenedor → profundidad 1
    return 1;
}

// Interfaz pública Python → calcula la profundidad del objeto
std::size_t get_nesting_depth(py::object obj)
{
    std::unordered_set<PyObject*> visited;
    return _depth(obj, visited);
}

py::object export_to_json_optionally(const py::object& data, bool to_file = false, const std::string& filename = "output.json"){
    py::module json = py::module::import("json");
    py::str json_str = json.attr("dumps")(data, py::arg("indent") = 4);
    if(to_file){
        std::ofstream ofs(filename);
        if(!ofs.is_open()){
            throw std::runtime_error("No se puedo abrir el archivo JSON "+ filename);

        }
        ofs << std::string(json_str);
        ofs.close();
        return py::none();
    }else{
        return json_str;
    }
}


PYBIND11_MODULE(_pyramscope, m) {
    m.doc() = "Backend nativo de pyramscope";
    m.def("get_size", &get_size,
          "Tamaño superficial en bytes de un objeto Python (usa sys.getsizeof)");
    // Nueva función: get_id
    m.def("get_id", &get_id, "Devuelve la dirección de memoria del objeto (como entero)");
    m.def("get_attrs", &get_attrs, "Devuelve la lista de atributos del objeto");
    m.def("get_refs", &get_refs, "Devuelve los objetos que referencian al objeto dado");
    m.def("get_referents", &get_referents, "Devuelve objetos a los que el objeto apunta");
    m.def("get_aliases", &get_aliases, "Encuentra alias del objeto en memoria");
    m.def("deep_size", &deep_size,"Tamaño total recursivo del objeto, sin doble conteo (alias/ciclos)");
    m.def("get_top_heavy_objects", &get_top_heavy_objects);
    m.def("get_nesting_depth", &get_nesting_depth,"Devuelve la profundidad máxima de anidamiento del objeto");
    m.def("export_to_json_optionally", &export_to_json_optionally,
        py::arg("data"),
        py::arg("to_file") = false,
        py::arg("filename") = "output.json");
  

  


}