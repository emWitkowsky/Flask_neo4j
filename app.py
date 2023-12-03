from flask import Flask, jsonify, request
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

uri = os.getenv('URI')
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
# driver = AsyncGraphDatabase.driver(uri, auth=(user, password), database='neo4j')
driver = AsyncGraphDatabase.driver("neo4j+s://f56be023.databases.neo4j.io", auth=("neo4j", "4u5ZZKSbiMb4JqdwzzESqUB700G6cLrRvwX0D2HhK-4"), database='neo4j')


# pobieranie wszystkich pracowników z możliwością sortowania i filtrowania
async def get_employees(tx, filter_key, filter_value, order_by, order_direction):
    query = "MATCH (e:Employee)"

    if filter_key and filter_value:
        query += f" WHERE e.{filter_key}='{filter_value}'"

    if order_by:
        query += f" RETURN e, ID(e) ORDER BY e.{order_by} {order_direction}"
    else:
        query += " RETURN e, ID(e)"

    results = await tx.run(query)
    records = await results.data()
    employees = [{'id': record['ID(e)'],
                  'name': record['e']['name'],
                  'surname': record['e']['surname'],
                  'position': record['e']['position']} for record in records]

    return employees


@app.route('/employees', methods=['GET'])
async def get_employees_route():
    filter_key = request.args.get('filterkey')
    filter_value = request.args.get('filterval')
    order_by = request.args.get('order')
    order_direction = request.args.get('direction', 'ASC')

    async with driver.session() as session:
        employees = await session.read_transaction(get_employees, filter_key, filter_value, order_by, order_direction)

    response = {'employees': employees}
    return jsonify(response)


# dodawanie nowego pracownika
async def add_employee(tx, name, surname, position, department_name, is_manager):
    query = ("MATCH (e:Employee {name: $name, surname: $surname}) RETURN e")
    result = await tx.run(query, name=name, surname=surname)
    existing_employee = await result.single()

    if existing_employee:
        return 'Employee with this name and surname already exists'

    if is_manager:
        query = (
            "MATCH (d:Department {department_name: $department_name}) "
            "CREATE (e:Employee {name: $name, surname: $surname, position: $position})"
            "CREATE (manager:Employee {name: 'Manager', surname: 'Surname'}) "
            "CREATE (manager) - [:MANAGES] -> (e) - [:WORKS_IN] -> (d)"
            "RETURN e"
        )
        await tx.run(query, name=name, surname=surname, position=position, department_name=department_name)
    else:
        query = (
            "MATCH (d:Department {department_name: $department_name}) "
            "CREATE (e:Employee {name: $name, surname: $surname, position: $position})"
            "CREATE (e) - [:WORKS_IN] -> (d)"
            "RETURN e"
        )
        await tx.run(query, name=name, surname=surname, position=position, department_name=department_name)

    return 'Employee added successfully'

# all emps
@app.route('/employees', methods=['POST'])
async def add_employee_route():
    name = request.json.get('name')
    surname = request.json.get('surname')
    position = request.json.get('position')
    department_name = request.json.get('department_name')
    is_manager = request.json.get('is_manager', False)

    if not name or not surname or not position or not department_name:
        response = {'error': 'Please provide name, surname, position, and department_name'}
        return jsonify(response), 400

    async with driver.session() as session:
        result = await session.write_transaction(add_employee, name, surname, position, department_name, is_manager)
        response = {'status': result}

        if "exists" in result.lower():
            return jsonify(response), 400

        return jsonify(response)


# update
async def update_employee(tx, id, new_name, new_surname, new_position, new_department):
    query = "MATCH (e:Employee) WHERE ID(e)=$id RETURN e"
    res = await tx.run(query, id=id)
    result = await res.data()

    if not result:
        return None
    else:
        set_queries = []
        params = {'id': id}

        if new_name:
            set_queries.append('e.name = $new_name')
            params['new_name'] = new_name

        if new_surname:
            set_queries.append('e.surname = $new_surname')
            params['new_surname'] = new_surname

        if new_position:
            set_queries.append('e.position = $new_position')
            params['new_position'] = new_position

        set_clause = ', '.join(set_queries)

        if set_clause:
            set_clause = f"SET {set_clause}"

        tx.run(f"MATCH (e:Employee) WHERE ID(e)=$id {set_clause}", **params)

        if new_department:
            query += (
                "MATCH (e)-[:WORKS_IN]->(oldD:Department) WHERE ID(e)=$id "
                "MATCH (newD:Department {department_name: $new_department}) "
                "MERGE (e)-[:WORKS_IN]->(newD) "
            )
            await tx.run(query, id=id, new_name=new_name, new_surname=new_surname, new_position=new_position,
                         new_department=new_department)

        return {'name': new_name, 'surname': new_surname, 'position': new_position}


@app.route('/employees/<int:id>', methods=['PUT'])
async def update_employee_route(id):
    new_name = request.json.get('name')
    new_surname = request.json.get('surname')
    new_position = request.json.get('position')
    new_department = request.json.get('department')

    # check if data to update
    if not new_name and not new_surname and not new_position and not new_department:
        response = {'error': 'Provide at least one field to update'}
        return jsonify(response), 400

    async with driver.session() as session:
        employee = await session.write_transaction(update_employee, id, new_name, new_surname, new_position,
                                                   new_department)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


# usuwanie pracownika i, jeśli pracownik jest managerem, zmiana managera lub usunięcie departamentu
async def delete_employee(tx, id):
    query = "MATCH (e:Employee) WHERE ID(e) = $id DETACH DELETE e"
    await tx.run(query, id=id)

    return {'id': id}


@app.route('/employees/<int:id>', methods=['DELETE'])
async def delete_employee_route(id):
    async with driver.session() as session:
        employee = await session.write_transaction(delete_employee, id)

    if not employee:
        response = {'message': 'Employee not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


# subs of manager
async def get_subordinates(tx, id):
    query = (
        "MATCH (employee:Employee)-[:MANAGES]->(subordinate:Employee) "
        "WHERE ID(employee) = $id "
        "RETURN subordinate"
    )

    result = await tx.run(query, id=id)
    subordinates = [record['subordinate'] for record in await result.data()]
    return subordinates


@app.route('/employees/<int:id>/subordinates', methods=['GET'])
async def get_subordinates_route(id):
    async with driver.session() as session:
        subordinates = await session.read_transaction(get_subordinates, id)

    if not subordinates:
        response = {'message': 'Employee has no subs or hes 404'}
        return jsonify(response), 404
    else:
        response = {'subordinates': subordinates}
        return jsonify(response)


# Department of the employee
async def get_employee_department_info(tx, id):
    query = (
        "MATCH (employee:Employee)-[:WORKS_IN]->(department:Department) "
        "WHERE ID(employee) = $id "
        "OPTIONAL MATCH (department)<-[:WORKS_IN]-(employees:Employee) "
        "WITH department, count(employees) AS number_of_employees "
        "RETURN department.department_name AS department_name, "
        "number_of_employees"
    )

    result = await tx.run(query, id=id)
    department_info = await result.data()

    if department_info:
        department_data = department_info[0]
        manager_query = (
            "MATCH (manager:Employee)-[:MANAGES]->(employee:Employee) "
            "WHERE ID(employee) = $id "
            "RETURN manager"
        )
        manager_result = await tx.run(manager_query, id=id)
        manager_data = await manager_result.single()

        if manager_data:
            manager = {
                'name': manager_data['manager']['name'],
                'surname': manager_data['manager']['surname']
            }
            department_data['manager'] = manager
        else:
            department_data['manager'] = None

        return department_data
    else:
        return None


@app.route('/employees/<int:id>/department', methods=['GET'])
async def get_employee_department_info_route(id):
    async with driver.session() as session:
        department_info = await session.read_transaction(get_employee_department_info, id)

    if not department_info:
        response = {'message': '404: Employee not found'}
        return jsonify(response), 404
    else:
        return jsonify(department_info)


# departments with additional conditioning
async def get_departments(tx, filter_by, order_by, order_direction):
    query = (
        "MATCH (d:Department) "
        "OPTIONAL MATCH (d)<-[:WORKS_IN]-(employees:Employee) "
        "WITH d, count(employees) AS number_of_employees "
    )

    if filter_by:
        query += f"WHERE d.department_name CONTAINS '{filter_by}' "

    query += "RETURN ID(d) as id, d.department_name AS department, number_of_employees"

    if order_by:
        query += f" ORDER BY {order_by} {order_direction}"

    res = await tx.run(query)
    result = await res.data()
    return result


@app.route('/departments', methods=['GET'])
async def get_departments_route():
    filter_by = request.args.get('filter')
    order_by = request.args.get('order')
    order_direction = request.args.get('direction', 'ASC')

    async with driver.session() as session:
        departments = await session.read_transaction(get_departments, filter_by, order_by, order_direction)

    return jsonify({'departments': departments})


# All the workers of this world (unite)
async def get_department_employees(tx, id):
    query = (
        "MATCH (department:Department)<-[:WORKS_IN]-(employee:Employee) "
        "WHERE ID(department) = $id "
        "RETURN employee"
    )
    res = await tx.run(query, id=id)
    result = await res.data()
    return result


@app.route('/departments/<int:id>/employees', methods=['GET'])
async def get_department_employees_route(id):
    async with driver.session() as session:
        department_employees = await session.read_transaction(get_department_employees, id)

    if not department_employees:
        response = {'message': 'Department has no employees'}
        return jsonify(response), 404
    else:
        return jsonify({'employees': department_employees})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)