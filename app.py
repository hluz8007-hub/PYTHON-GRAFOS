from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import networkx as nx
import io, base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

# -------------------------------
# Clase Árbol Binario
# -------------------------------
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izq = None
        self.der = None

class ArbolBinario:
    def __init__(self):
        self.raiz = None

    def insertar(self, valor):
        if self.raiz is None:
            self.raiz = Nodo(valor)
        else:
            self._insertar(self.raiz, valor)

    def _insertar(self, nodo, valor):
        if valor < nodo.valor:
            if nodo.izq is None:
                nodo.izq = Nodo(valor)
            else:
                self._insertar(nodo.izq, valor)
        else:
            if nodo.der is None:
                nodo.der = Nodo(valor)
            else:
                self._insertar(nodo.der, valor)

    def inorden(self, nodo):
        return self.inorden(nodo.izq) + [nodo.valor] + self.inorden(nodo.der) if nodo else []

    def preorden(self, nodo):
        return [nodo.valor] + self.preorden(nodo.izq) + self.preorden(nodo.der) if nodo else []

    def postorden(self, nodo):
        return self.postorden(nodo.izq) + self.postorden(nodo.der) + [nodo.valor] if nodo else []

    def dibujar(self):
        G = nx.Graph()
        def agregar_nodos(nodo):
            if nodo:
                if nodo.izq:
                    G.add_edge(nodo.valor, nodo.izq.valor)
                    agregar_nodos(nodo.izq)
                if nodo.der:
                    G.add_edge(nodo.valor, nodo.der.valor)
                    agregar_nodos(nodo.der)
        agregar_nodos(self.raiz)
        fig, ax = plt.subplots()
        nx.draw(G, with_labels=True, node_color="#27ae60", node_size=900,
                font_size=12, font_color="white", edge_color="#2c3e50", width=2, ax=ax)
        return fig, len(G.nodes)

# -------------------------------
# Ruta principal
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    graph_img = None
    recorridos = None
    cantidad = None
    matriz = None
    recorrido = None
    ruta = None

    if request.method == "POST":
        action = request.form["action"]

        # ----- Grafos -----
        if action == "grafo":
            edges_text = request.form["edges"]
            edges = [tuple(e.strip().split("-")) for e in edges_text.split(",")]

            G = nx.Graph()
            G.add_edges_from(edges)

            # Matriz de adyacencia
            nodos = list(G.nodes)
            matriz = ""
            for i in nodos:
                fila = []
                for j in nodos:
                    fila.append(1 if G.has_edge(i, j) else 0)
                matriz += str(fila) + "\n"

            # Recorrido BFS
            start = request.form["start"]
            if start in G.nodes:
                recorrido = list(nx.bfs_tree(G, start).nodes)

            # Mejor ruta
            path_text = request.form["path"]
            if path_text:
                origen, destino = path_text.split(",")
                if origen in G.nodes and destino in G.nodes:
                    try:
                        ruta = nx.shortest_path(G, origen, destino)
                    except:
                        ruta = "No existe ruta"

            # Dibujar grafo
            fig, ax = plt.subplots()
            nx.draw(G, with_labels=True, node_color="#e67e22", node_size=900,
                    font_size=12, font_color="white", edge_color="#2980b9", width=2, ax=ax)

            canvas = FigureCanvas(fig)
            img = io.BytesIO()
            canvas.print_png(img)
            graph_img = base64.b64encode(img.getvalue()).decode()
            cantidad = len(G.nodes)

        # ----- Árboles -----
        elif action == "arbol":
            values_text = request.form["values"]
            values = [int(v.strip()) for v in values_text.split(",")]

            arbol = ArbolBinario()
            for v in values:
                arbol.insertar(v)

            fig, cantidad = arbol.dibujar()
            canvas = FigureCanvas(fig)
            img = io.BytesIO()
            canvas.print_png(img)
            graph_img = base64.b64encode(img.getvalue()).decode()

            recorridos = {
                "inorden": arbol.inorden(arbol.raiz),
                "preorden": arbol.preorden(arbol.raiz),
                "postorden": arbol.postorden(arbol.raiz)
            }

    return render_template("index.html", graph=graph_img, recorridos=recorridos,
                           cantidad=cantidad, matriz=matriz, recorrido=recorrido, ruta=ruta)

if __name__ == "__main__":
    app.run(debug=True)


