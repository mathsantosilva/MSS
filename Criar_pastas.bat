@echo off
REM Script para criar a estrutura de pastas do projeto Python modularizado

set ROOT=seu_projeto

REM raiz
mkdir %ROOT%
mkdir %ROOT%\app
mkdir %ROOT%\core
mkdir %ROOT%\domain
mkdir %ROOT%\domain\documents
mkdir %ROOT%\domain\redis_ops
mkdir %ROOT%\domain\bancos
mkdir %ROOT%\domain\empresas
mkdir %ROOT%\domain\versions
mkdir %ROOT%\use_cases
mkdir %ROOT%\ui
mkdir %ROOT%\ui\screens
mkdir %ROOT%\services
mkdir %ROOT%\tests
mkdir %ROOT%\tests\core
mkdir %ROOT%\tests\domain
mkdir %ROOT%\tests\use_cases
mkdir %ROOT%\tests\ui

echo Estrutura criada com sucesso em %ROOT%.
pause
