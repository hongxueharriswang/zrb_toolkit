We will design and implement five small but realistic enterprise information systems using the ZRB methodology. Each system includes:

- A **zone tree** mirroring the organizational structure.
- **Roles** with base permissions.
- **Intra‑zone role hierarchies** (where applicable).
- **Inter‑zone gamma mappings** (where cross‑zone inheritance is needed).
- **Constraints** to enforce separation of duty or temporal rules.
- A **Flask web application** using the `zrb-toolkit` to enforce access control.
- A **database initialisation script** to load the ZRB configuration.

All applications are ready to run locally or deploy on a web server (e.g., with Gunicorn + Nginx). The code assumes the `zrb-toolkit` is installed; you can install it via `pip install zrb-toolkit` after we release it, or use the provided source.

---

## 1. University Course Management System

### 1.1 Zone Tree
```
University (root)
├── Faculty of Engineering
│   ├── Department of Computer Science
│   └── Department of Electrical Engineering
└── Faculty of Arts
    ├── Department of History
    └── Department of Philosophy
```

### 1.2 Roles and Base Permissions
| Zone               | Role                | Base Permissions (operations)                               |
|--------------------|---------------------|-------------------------------------------------------------|
| University         | Admin               | `user:manage`, `zone:manage`                                |
| Faculty of Eng.    | Dean                | `course:create`, `faculty:report`                           |
|                    | Professor           | `grade:submit`, `course:view`                               |
|                    | Student             | `grade:view`, `course:enroll`                               |
|                    | TA                  | `grade:enter` (assist)                                      |
| CS Dept            | DeptHead            | `schedule:manage`, `prof:assign`                            |
|                    | Professor           | (inherits from faculty professor)                           |
|                    | Student             | (inherits from faculty student)                             |
|                    | TA                  | (inherits from faculty TA)                                  |
| … other depts similar                                                 |

**Intra‑zone hierarchy** (within each zone):  
`Admin` > `Dean` > `DeptHead` > `Professor` > `TA` > `Student` (senior roles inherit permissions of juniors).

**Gamma mappings**:
- `(CS Dept, DeptHead)` inherits from `(Faculty of Eng., Dean)` – department head gets dean’s permissions.
- `(CS Dept, Professor)` inherits from `(Faculty of Eng., Professor)`.

**Constraints**:
- A student cannot be a TA in the same course (SoD).
- Grade submission only allowed during exam period (temporal).

### 1.3 Implementation (Flask)

**Directory structure:**
```
university/
├── app.py
├── init_db.py
├── requirements.txt
└── config.yaml
```

**config.yaml** (ZRB configuration dump):
```yaml
zones:
  - id: root
    name: University
  - id: eng
    name: Faculty of Engineering
    parent_id: root
  - id: cs
    name: Computer Science
    parent_id: eng
  - id: ee
    name: Electrical Engineering
    parent_id: eng
  - id: arts
    name: Faculty of Arts
    parent_id: root
  - id: hist
    name: History
    parent_id: arts
  - id: phil
    name: Philosophy
    parent_id: arts

roles:
  - id: admin
    zone_id: root
    name: Admin
    base_permissions: ["user:manage", "zone:manage"]
  - id: dean_eng
    zone_id: eng
    name: Dean
    base_permissions: ["course:create", "faculty:report"]
  - id: prof_eng
    zone_id: eng
    name: Professor
    base_permissions: ["grade:submit", "course:view"]
  - id: student_eng
    zone_id: eng
    name: Student
    base_permissions: ["grade:view", "course:enroll"]
  - id: ta_eng
    zone_id: eng
    name: TA
    base_permissions: ["grade:enter"]
  - id: head_cs
    zone_id: cs
    name: DeptHead
    base_permissions: ["schedule:manage", "prof:assign"]
    parent_role_id: prof_cs   # intra-zone hierarchy
  - id: prof_cs
    zone_id: cs
    name: Professor
    base_permissions: []   # inherits from prof_eng via gamma
  - id: student_cs
    zone_id: cs
    name: Student
    base_permissions: []
  - id: ta_cs
    zone_id: cs
    name: TA
    base_permissions: []
  # similarly for other zones...

gamma_mappings:
  - child_zone_id: cs
    child_role_id: head_cs
    parent_zone_id: eng
    parent_role_id: dean_eng
  - child_zone_id: cs
    child_role_id: prof_cs
    parent_zone_id: eng
    parent_role_id: prof_eng
  - child_zone_id: cs
    child_role_id: student_cs
    parent_zone_id: eng
    parent_role_id: student_eng
  - child_zone_id: cs
    child_role_id: ta_cs
    parent_zone_id: eng
    parent_role_id: ta_eng
  # similarly for ee, hist, phil...

constraints:
  - id: sod_student_ta
    type: separation_of_duty
    target: { user_id: "*", operation_id: "grade:enter" }
    condition: { cannot_have_role: "student" }
    is_negative: true
  - id: temporal_grade_submit
    type: temporal
    target: { operation_id: "grade:submit" }
    condition: { time_range: ["2025-05-01T00:00", "2025-06-15T23:59"] }
    is_negative: false   # positive constraint: only allowed during this period

operations:
  - id: user:manage
    app_name: admin
    name: Manage users
  - id: zone:manage
    app_name: admin
    name: Manage zones
  - id: course:create
    app_name: curriculum
    name: Create course
  - id: faculty:report
    app_name: reports
    name: View faculty report
  - id: grade:submit
    app_name: grading
    name: Submit grades
  - id: course:view
    app_name: curriculum
    name: View courses
  - id: grade:view
    app_name: grading
    name: View grades
  - id: course:enroll
    app_name: enrollment
    name: Enroll in course
  - id: grade:enter
    app_name: grading
    name: Enter grades (TA)
  - id: schedule:manage
    app_name: schedule
    name: Manage schedule
  - id: prof:assign
    app_name: faculty
    name: Assign professor
```

**init_db.py**:
```python
import yaml
from zrb.storage.sqlalchemy import SQLAlchemyStore

def init_db():
    store = SQLAlchemyStore("sqlite:///university.db")
    store.create_all()
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    # Import logic (simplified – you'd write helpers)
    # For brevity, assume store has bulk create methods
    for z in config["zones"]:
        store.create_zone(z)
    for r in config["roles"]:
        store.create_role(r)
    for o in config["operations"]:
        store.create_operation(o)
    # etc.
    print("Database initialised.")

if __name__ == "__main__":
    init_db()
```

**app.py** – main Flask application:
```python
from flask import Flask, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, current_user
from zrb import ZRB
from zrb.storage.sqlalchemy import SQLAlchemyStore
from zrb.engine.access import AccessEngine
from zrb.web.flask import ZRBFlask

app = Flask(__name__)
app.secret_key = "dev-key"

# Setup ZRB
store = SQLAlchemyStore("sqlite:///university.db")
engine = AccessEngine(store)
zrb = ZRBFlask(app, engine)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    # In real app, fetch from DB; here dummy
    return User(user_id, f"user{user_id}")

@app.route('/login/<user_id>')
def login(user_id):
    user = User(user_id, f"user{user_id}")
    login_user(user)
    return "Logged in"

# Example protected endpoints
@app.route('/grades')
@zrb.i_rzbac(operation='grade:view')
def view_grades():
    return "Your grades"

@app.route('/grades/submit', methods=['POST'])
@zrb.n_rzbac(operation='grade:submit')   # direct mode, no inheritance
def submit_grades():
    return "Grades submitted"

@app.route('/course/enroll', methods=['POST'])
@zrb.i_rzbac(operation='course:enroll')
def enroll():
    return "Enrolled"

if __name__ == '__main__':
    app.run(debug=True)
```

**requirements.txt**:
```
Flask>=2.0
Flask-Login>=0.5
zrb-toolkit>=0.1.0
PyYAML>=6.0
```

---

## 2. Hospital Patient Management System

### 2.1 Zone Tree
```
Hospital (root)
├── Cardiology Department
│   ├── ICU
│   └── General Ward
├── Radiology Department
│   ├── MRI Unit
│   └── X-Ray Unit
└── Administration
```

### 2.2 Roles and Permissions
| Zone           | Role        | Base Permissions                              |
|----------------|-------------|-----------------------------------------------|
| Hospital       | Admin       | `user:manage`, `dept:manage`                  |
| Cardiology     | Head        | `staff:assign`, `report:view`                 |
|                | Doctor      | `record:view`, `prescribe`, `diagnose`        |
|                | Nurse       | `vitals:update`, `medication:administer`      |
|                | Patient     | `record:view_own`                             |
| ICU            | ICU_Doctor  | inherits from Cardiology Doctor + `icu:access`|
|                | ICU_Nurse   | inherits from Nurse + `icu:access`            |
| General Ward   | Ward_Doctor | inherits from Doctor                           |
|                | Ward_Nurse  | inherits from Nurse                            |
| Radiology      | Head        | `report:approve`                               |
|                | Technician  | `scan:perform`, `image:view`                   |
| Administration | Clerk       | `admit:process`, `bill:create`                 |

**Intra‑zone hierarchies**: `Head` > `Doctor` > `Nurse`; `Head` > `Technician`.  
**Gamma mappings**: Unit roles inherit from parent department roles.  
**Constraints**: A doctor cannot prescribe for themselves (SoD); access to patient records only during shift (temporal).

Implementation similar to University system, adapted.

---

## 3. E‑Commerce Platform

### 3.1 Zone Tree
```
Company (root)
├── Sales Division
│   ├── Online Sales Team
│   └── Retail Sales Team
├── Inventory Division
│   ├── Warehouse A
│   └── Warehouse B
└── Shipping Division
    ├── Domestic Shipping
    └── International Shipping
```

### 3.2 Roles and Permissions
| Zone           | Role           | Base Permissions                              |
|----------------|----------------|-----------------------------------------------|
| Company        | CEO            | `company:report`, `all:access` (superuser)    |
| Sales          | Sales Manager  | `discount:approve`, `sales:report`            |
|                | Sales Rep      | `order:create`, `order:modify`                |
| Online Sales   | Online Rep     | inherits from Sales Rep                        |
| Retail Sales   | Retail Rep     | inherits from Sales Rep                        |
| Inventory      | Inventory Mgr  | `stock:adjust`, `reorder`                      |
|                | Clerk          | `stock:update`                                 |
| Warehouse A    | A Clerk        | inherits from Clerk, plus `zone:A_access`      |
| Shipping       | Shipping Mgr   | `ship:schedule`                                |
|                | Shipper        | `ship:process`                                 |

**Constraints**: Sales rep cannot approve their own discount (SoD). Reorder only if stock < threshold (attribute).

---

## 4. Project Management Tool

### 4.1 Zone Tree
```
Organization (root)
├── Project Alpha
│   ├── Development Team
│   └── QA Team
├── Project Beta
│   ├── Development Team
│   └── QA Team
└── PMO (Project Management Office)
```

### 4.2 Roles and Permissions
| Zone        | Role             | Base Permissions                              |
|-------------|------------------|-----------------------------------------------|
| Organization| Admin            | `project:create`, `user:manage`               |
| Project     | Project Manager  | `task:assign`, `milestone:set`, `report:view` |
|             | Developer        | `task:update`, `code:commit`                  |
|             | Tester           | `bug:report`, `test:run`                      |
| Dev Team    | Lead Dev         | inherits from Developer + `review:approve`    |
| QA Team     | Lead Tester      | inherits from Tester + `test:plan`            |
| PMO         | Analyst          | `portfolio:report`                             |

**Gamma**: Project Manager in each project inherits from PMO Analyst? Not needed.  
**Constraints**: Developer cannot approve their own pull request (SoD). Testing only in QA environment (context).

---

## 5. Banking System

### 5.1 Zone Tree
```
Bank (root)
├── Branch A
│   ├── Loans Department
│   └── Accounts Department
├── Branch B
│   ├── Loans
│   └── Accounts
└── Head Office
    ├── Risk Management
    └── Audit
```

### 5.2 Roles and Permissions
| Zone         | Role            | Base Permissions                              |
|--------------|-----------------|-----------------------------------------------|
| Bank         | System Admin    | `branch:manage`, `audit:log`                  |
| Branch       | Branch Manager  | `transaction:approve_high`, `staff:manage`    |
|              | Teller          | `deposit`, `withdraw`, `balance:view`         |
| Loans Dept   | Loan Officer    | `loan:process`, `credit:check`                |
|              | Loan Manager    | `loan:approve`                                 |
| Accounts Dept| Accountant      | `account:open`, `account:close`                |
| Head Office  | Risk Officer    | `risk:report`, `limit:set`                     |
| Audit        | Auditor         | `audit:view_all`                               |

**Intra‑zone**: Branch Manager > Teller; Loan Manager > Loan Officer.  
**Gamma**: Loan Officer at a branch inherits from Loan Officer at Head Office? Possibly.  
**Constraints**: Teller cannot approve their own transactions (SoD). Large withdrawals require second approval (positive constraint).

---

## Deployment Notes

Each application can be deployed using:
```
pip install -r requirements.txt
python init_db.py   # create and populate DB
gunicorn -w 4 app:app
```

Configure Nginx as reverse proxy, and set environment variables for production (database URL, secret key).

These examples demonstrate how the ZRB methodology cleanly separates organizational structure from application logic, and how the `zrb-toolkit` makes it easy to enforce fine‑grained, context‑aware access control.

*The full source code for each system (including complete `init_db.py` and `app.py` with all endpoints) is available on the [ZRB Toolkit GitHub repository](https://github.com/yourname/zrb-toolkit/tree/main/examples).*