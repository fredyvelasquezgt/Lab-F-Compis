import copy
import pandas as pd
from tabulate import tabulate
from ALR0 import *


class SLRTable(ALR0):
    def __init__(self, productions, subsets_, subsets_iterations, transitions):
        #Inicializamos la clase padre
        super().__init__()
        #Creamos la variable que se va a utilizar para las transiciones
        self.transitions = transitions
        #Creamos la variable que se va a utilizar para las producciones
        self.productions = productions
        #Creamos la variable que se va a utilizar para los conjuntos
        self.subsets_ = subsets_
        #Lista que nos ayudará con el número de conjuntos
        self.subsets_iterations = subsets_iterations
        #Se declara una lista para almacenar los no terminales encontrados
        self.non_terminals_result = list()
        #Lista que utilizaremos para almacenar el resultado del firts
        self.first_result = list()
        #Lista que utilizaremos para almacenar el resultado de action, y así tener los componentes
        self.action_components_result_list = list()
        #Lista que utilizaremos para almacenar el resultado del action
        self.list_action_result_compute = list()
        #Lista que utilizaremos para almacenar el resultado de goto, y así tener los componentes
        self.goto_components_result_list = list()
        #Lista para almacenar el resultado del goto
        self.goto_result = list()
        #Instanciamos la función para encontrar los no terminales
        self.find_non_terminals()
        
    def find_transitions(self, review_transition):
        # Inicializar un conjunto para almacenar las transiciones
        transitions = set()
        # Crear un conjunto de símbolos de revisión
        review_symbols = set(review_transition)
        # Filtrar las reglas que contienen símbolos de revisión
        filtered_rules = [rule for rule in self.productions if any(symbol in review_symbols for symbol in rule[1])]
        # Iterar sobre las reglas filtradas
        for rule in filtered_rules:
            # Encontrar el siguiente símbolo después de cada ocurrencia de un símbolo de revisión
            for index, symbol in enumerate(rule[1]):
                if symbol in review_symbols and index + 1 < len(rule[1]) and rule[1][index+1] not in self.non_terminals_result:
                    # Añadir el siguiente símbolo a las transiciones
                    transitions.add(rule[1][index+1])
        # Devolver el conjunto de transiciones
        return transitions

    def get_construction_table(self):
        # Removemos el punto de las producciones 
        self.remove_point()
        # Primero dividirlos por sus secciones correspondientes
        lowercase_set = set()
        uppercase_set = set()
        for x in self.transitions:
            if x[1].islower():
                # Agrega x[1] al conjunto lowercase_set si x[1] es una letra minúscula
                lowercase_set.add(x[1])
            else:
                # Agrega x[1] al conjunto uppercase_set si x[1] es una letra mayúscula
                uppercase_set.add(x[1])
        # Crea una lista de los componentes de goto que no están en goto_components_result_list
        self.goto_components_result_list = list(lowercase_set - set(self.goto_components_result_list))
        # Crea una lista de los componentes de action que no están en action_components_result_list
        self.action_components_result_list = list(uppercase_set - set(self.action_components_result_list))
        # Ordena la lista de componentes de action en orden descendente
        self.action_components_result_list.sort(reverse=True)
        # Llena la tabla de goto utilizando los subconjuntos, los componentes de goto y las transiciones
        self.goto_result = [[x, y, z[2]] for x in self.subsets_iterations for y in self.goto_components_result_list for z in self.transitions if z[0] == x and z[1] == y]
        # Genera la lista de resultados de action utilizando los subconjuntos, los componentes de action y las transiciones
        self.list_action_result_compute = self.generate_list_action_result_compute()
        # Obtiene los primeros (FIRST) para cada símbolo no terminal en self.productions
        self.first_result = [[x[0], self.First(x[0])] for x in self.productions if [x[0], self.First(x[0])] not in self.first_result]
        # Genera la lista de resultados de action utilizando la función generate_action_follow_replace
        self.generate_action_follow_replace()

    #Función que se encargará de buscar los no terminales
    def find_non_terminals(self):
        # Itera sobre cada producción en la lista de producciones
        for x in self.productions:
            # Revisa si el primer elemento de la producción no está en la lista de símbolos no terminales
            if x[0] not in self.non_terminals_result:
                # Si no está, entonces lo agrega a la lista de símbolos no terminales
                self.non_terminals_result.append(x[0])

    
    def find_new_values(self, review_transition):
        # Inicializar un conjunto para almacenar los nuevos valores
        new_set = set()
        # Obtener todos los símbolos de las reglas en un solo conjunto
        symbols = set()
        for rule in self.productions:
            symbols.update(rule[1])
        # Iterar sobre los elementos en review_transition
        for symbol in review_transition:
            # Iterar sobre las reglas
            for rule in self.productions:
                # Si symbol está en la lista de símbolos de la regla
                if symbol in rule[1]:
                    # Encontrar el índice de symbol en la lista de símbolos de la regla
                    non_terminal_index = rule[1].index(symbol)
                    # Si non_terminal_index es igual a la longitud de la lista de símbolos de la regla menos uno
                    if non_terminal_index == len(rule[1])-1:
                        # Añadir el símbolo inicial de la regla al conjunto de nuevos valores
                        new_set.add(rule[0])
                    # Si el siguiente símbolo en la lista de símbolos de la regla está en los no terminales
                    elif rule[1][non_terminal_index+1] in self.non_terminals_result:
                        # Iterar sobre el conjunto de primeros símbolos
                        for first_symbol in self.first_result:
                            # Si el primer símbolo coincide con el siguiente símbolo en la lista de símbolos de la regla
                            if first_symbol[0] == rule[1][non_terminal_index+1]:
                                # Actualizar el conjunto de nuevos valores con el conjunto de primeros símbolos
                                new_set.update(first_symbol[1])
        # Devolver el conjunto de nuevos valores
        return new_set

    #Función para remover el punto de las producciones
    def remove_point(self):
        # Ubicamos el punto en las producciones y lo removemos
        for x in range(len(self.productions)):
            for y in range(len(self.productions[x][1])):
                if self.productions[x][1][y] == ".":
                    self.productions[x][1].remove(".")
                    break

    def generate_list_action_result_compute(self):
        # Crea una lista vacía para almacenar los resultados
        result = []
        # Itera sobre cada elemento en self.subsets_iterations
        for x in self.subsets_iterations:
            # Itera sobre cada elemento en self.action_components_result_list
            for y in self.action_components_result_list:
                # Itera sobre cada elemento en self.transitions
                for z in self.transitions:
                    # Revisa si z[0] es igual a x y z[1] es igual a y
                    if z[0] == x and z[1] == y:
                        # Si y es igual a "$", agrega [x, y, "acc"] a la lista de resultados
                        if y == "$":
                            result.append([x, y, "acc"])
                        # Si no, agrega [x, y, "s" + str(z[2])] a la lista de resultados
                        else:
                            result.append([x, y, "s" + str(z[2])])
        # Devuelve la lista de resultados
        return result
    
    def follow(self, state, accept_state):
        # Inicializar un conjunto con el estado
        revisar = {state}
        # Inicializar un conjunto para almacenar las transiciones
        transitions = set()
        # Ejecutar el bucle hasta que no haya cambios en revisar
        while True:
            # Guardar el estado actual de revisar en previous_revisar
            previous_revisar = set(revisar)
            # Encontrar nuevos valores a partir de revisar
            nuevos_revisar = self.find_new_values(revisar)
            # Actualizar revisar con los nuevos valores
            revisar.update(nuevos_revisar)
            # Actualizar las transiciones con las nuevas transiciones encontradas
            transitions.update(self.find_transitions(revisar))
            # Si revisar no ha cambiado, salir del bucle
            if revisar == previous_revisar:
                break
        # Si accept_state + "'" está en revisar, añadir el símbolo de aceptación al conjunto de transiciones
        if accept_state + "'" in revisar:
            transitions.add("$")
        # Devolver la lista de transiciones
        return list(transitions)

    def generate_action_follow_replace(self):
        result = []
        for first_element, subset in enumerate(self.subsets_):
            # Itera sobre los subconjuntos en self.subsets_ y sus elementos
            for second_element in subset:
                # Revisa si el último símbolo es un punto
                if second_element[1][-1] != ".":
                    continue
                indice = second_element[1].index(".")
                # Revisa si el símbolo anterior al punto es el primer símbolo de la primera producción
                if second_element[1][indice - 1] == self.productions[0][1][0]:
                    continue
                # Crea una nueva tupla con el mismo símbolo inicial y la cadena modificada
                tuple_symbol = [second_element[0], second_element[1][:indice] + second_element[1][indice+1:]]
                # Itera sobre las producciones en self.productions
                for z, production in enumerate(self.productions):
                    # Revisa si la tupla creada es igual a la producción actual
                    if production == tuple_symbol:
                        # Utiliza la función follow para obtener el conjunto de símbolos que pueden seguir a ese símbolo
                        transition = self.follow(tuple_symbol[0], self.productions[0][1][0])
                        # Agrega una nueva entrada a la lista result utilizando el índice del primer elemento del for loop exterior,
                        # el elemento actual de transition y una cadena que contiene "r" y el índice del elemento actual en self.productions
                        for w in transition:
                            result.append([first_element, w, "r" + str(z)])
        # Agrega la lista result a la lista self.list_action_result_compute
        self.list_action_result_compute += result

    def First(self, symbol):
        # Inicializar la lista visited con el símbolo proporcionado
        visited = [symbol]
        # Bucle infinito que se ejecuta hasta que no haya cambios en la lista visited
        while True:
            # Almacenar el tamaño inicial de la lista visited
            visit_initial = len(visited)
            # Iterar sobre cada elemento en la lista visited
            for y in visited:
                # Iterar sobre cada regla en self.productions
                for z in self.productions:
                    # Si el elemento visitado actual coincide con el primer elemento de la regla actual
                    if y == z[0]:
                        # Si el segundo elemento de la regla actual no está en la lista visited
                        if z[1][0] not in visited:
                            # Añadir el segundo elemento de la regla actual a la lista visited
                            visited.append(z[1][0])
            # Almacenar el tamaño final de la lista visited
            final_visit = len(visited)
            # Si el tamaño inicial y final de la lista visited son iguales, salir del bucle
            if visit_initial == final_visit:
                break
        # Crear una nueva lista added con los elementos de visited que también están en self.action_components_result_list
        added = [y for y in visited if y in self.action_components_result_list]
        # Devolver la lista added
        return added


    def print_table(self):
        # Create an empty DataFrame with the specified columns
        columns = self.action_components_result_list + self.goto_components_result_list
        df = pd.DataFrame(columns=columns)
        # Fill the table with data from 'goto' and 'action'
        for row, col, value in self.goto_result + self.list_action_result_compute:
            df.at[row, col] = value
        # Fill NaN values with empty strings
        df.fillna('', inplace=True)
        # Set the index column name
        df.index.name = 'state'
        # Remove the first element of each header tuple
        headers = [header for header in df.columns]
        # Set the modified headers to the DataFrame
        df.columns = headers
        # Sort it by state
        df.sort_index(inplace=True)
        # Convert the DataFrame to a table using the 'tabulate' library
        table = tabulate(df, headers='keys', tablefmt='grid', showindex=True)
        # Display the table in the console
        print(table)

