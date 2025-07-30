# 🔌 pyconnector

**pyconnector** is a flexible, pluggable Python package designed to connect seamlessly to popular databases and services including Databricks, PostgreSQL, SMTP, and SFTP — using JDBC, ODBC, or native protocols.

## ✨ Features

- ✅ Multi-system support: Databricks, Postgres, SMTP, SFTP  
- 🔄 Multi-mode: JDBC and ODBC connectors  
- ⚙️ Dynamic driver versioning and loading  
- 📦 Lightweight, modular, and extensible  
- 🧩 Easy to plug in new systems  

## 📦 Installation

```bash
pip install pyconnector


# 🔌 Included Connectors
Databricks

JDBC Connector

ODBC Connector

PostgreSQL

JDBC Connector

ODBC Connector

SMTP

Basic email sending support

SFTP

File upload/download over SSH



#  Driver Management
All JDBC/ODBC drivers are stored in the local /drivers directory and loaded dynamically by:

system (e.g., databricks, postgres)

driver_type (jdbc or odbc)

version (optional; defaults to latest)