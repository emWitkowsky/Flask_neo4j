// pracownicy
CREATE (e1:Employee {name: "Jonathan", surname: "Goldberg", position: "developer"})
CREATE (e2:Employee {name: "Jack", surname: "Black", position: "developer"})
CREATE (e3:Employee {name: 'Percy', surname: 'Jackson', position: 'developer'})
CREATE (e4:Employee {name: 'Thor', surname: 'Odinson', position: 'developer'})
CREATE (e5:Employee {name: 'Mike', surname: 'Magic', position: 'developer'})
CREATE (e6:Employee {name: 'Mikel', surname: 'Arteta', position: 'manager'})
CREATE (e7:Employee {name: 'Sarah', surname: 'Connor', position: 'manager'})
CREATE (e8:Employee {name: 'Lee', surname: 'Sin', position: 'manager'})
CREATE (e9:Employee {name: 'Jennifer', surname: 'Lawrence', position: 'manager'})
CREATE (e10:Employee {name: 'Jerry', surname: 'Mouse', position: 'manager'})
CREATE (e11:Employee {name: 'Tom', surname: 'Cat', position: 'consultant'})
CREATE (e12:Employee {name: 'William', surname: 'Stone', position: 'consultant'})
CREATE (e13:Employee {name: 'Dwayne', surname: 'Rock', position: 'consultant'})
CREATE (e14:Employee {name: 'John', surname: 'Pope', position: 'consultant'})
CREATE (e15:Employee {name: 'Tom', surname: 'Hiddlestone', position: 'consultant'})
CREATE (e16:Employee {name: 'Tom', surname: 'Cruise', position: 'HR'})
CREATE (e17:Employee {name: 'Ava', surname: 'Angel', position: 'HR'})
CREATE (e18:Employee {name: 'Rick', surname: 'Prime', position: 'HR'})
CREATE (e19:Employee {name: 'Adonis', surname: 'Greek', position: 'HR'})
CREATE (e20:Employee {name: 'Russell', surname: 'Crowe', position: 'HR'})
CREATE (e21:Employee {name: 'Anthony', surname: 'Hopkins', position: 'receptionist'})
CREATE (e22:Employee {name: 'Elijah', surname: 'Wood', position: 'receptionist'})
CREATE (e23:Employee {name: 'Emma', surname: 'Watson', position: 'receptionist'})
CREATE (e24:Employee {name: 'Luke', surname: 'Skywalker', position: 'receptionist'})
CREATE (e25:Employee {name: 'Odel', surname: 'Martell', position: 'receptionist'})
CREATE (e26:Employee {name: 'Jon', surname: 'Snow', position: 'intern'})
CREATE (e27:Employee {name: 'Daemon', surname: 'Targaryen', position: 'intern'})
CREATE (e28:Employee {name: 'Conan', surname: 'Barbarian', position: 'intern'})
CREATE (e29:Employee {name: 'Morty', surname: 'Smith', position: 'intern'})
CREATE (e30:Employee {name: 'Rick', surname: 'Sanchez', position: 'intern'})

// departamenty
CREATE (d1:Department {department_name: 'IT'})
CREATE (d2:Department {department_name: 'Management'})
CREATE (d3:Department {department_name: 'CustomerHelp'})
CREATE (d4:Department {department_name: 'Registration'})
CREATE (d5:Department {department_name: 'Internship'})
CREATE (d6:Department {department_name: 'HumanResources'})

// ustawienie relacji WORKS_IN
//IT
CREATE
  (e1) - [:WORKS_IN] -> (d1),
  (e2) - [:WORKS_IN] -> (d1),
  (e3) - [:WORKS_IN] -> (d1),
  (e4) - [:WORKS_IN] -> (d1),
  (e5) - [:WORKS_IN] -> (d1)
//  (e6) - [:WORKS_IN] -> (d1)

CREATE
  (e6) - [:WORKS_IN] -> (d2),
  (e7) - [:WORKS_IN] -> (d2),
  (e8) - [:WORKS_IN] -> (d2),
  (e9) - [:WORKS_IN] -> (d2),
  (e10) - [:WORKS_IN] -> (d2)

CREATE
  (e11) - [:WORKS_IN] -> (d3),
  (e12) - [:WORKS_IN] -> (d3),
  (e13) - [:WORKS_IN] -> (d3),
  (e14) - [:WORKS_IN] -> (d3),
  (e15) - [:WORKS_IN] -> (d3)

CREATE
  (e16) - [:WORKS_IN] -> (d6),
  (e17) - [:WORKS_IN] -> (d6),
  (e18) - [:WORKS_IN] -> (d6),
  (e19) - [:WORKS_IN] -> (d6),
  (e20) - [:WORKS_IN] -> (d6)

CREATE
  (e26) - [:WORKS_IN] -> (d5),
  (e27) - [:WORKS_IN] -> (d5),
  (e28) - [:WORKS_IN] -> (d5),
  (e29) - [:WORKS_IN] -> (d5),
  (e30) - [:WORKS_IN] -> (d5)

CREATE
  (e21) - [:WORKS_IN] -> (d4),
  (e22) - [:WORKS_IN] -> (d4),
  (e23) - [:WORKS_IN] -> (d4),
  (e24) - [:WORKS_IN] -> (d4),
  (e25) - [:WORKS_IN] -> (d4)

// relacja MANAGES

FOREACH (emp IN [e1, e2, e3, e4, e5] |
  MERGE (e6) - [:MANAGES] -> (emp)
)

FOREACH (emp IN [e11, e12, e13, e14, e15] |
  MERGE (e7) - [:MANAGES] -> (emp)
)

FOREACH (emp IN [e16, e17, e18, e19, e20] |
  MERGE (e8) - [:MANAGES] -> (emp)
)

FOREACH (emp IN [e21, e22, e23, e24, e25] |
  MERGE (e9) - [:MANAGES] -> (emp)
)

FOREACH (emp IN [e26, e27, e28, e29, e30] |
  MERGE (e10) - [:MANAGES] -> (emp)
)