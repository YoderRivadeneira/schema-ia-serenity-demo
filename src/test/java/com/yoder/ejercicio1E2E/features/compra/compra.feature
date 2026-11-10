Feature: Flujo de compra en SauceDemo

  Scenario Outline: Completar una compra satisfactoriamente
    Given el usuario se logea con "<usuario>" y "<password>"
    When el usuario agrega dos productos al carrito
    And procede al checkout de los productos agregados al carrito
    And completa el formulario de compra con "<nombre>", "<apellido>" y "<codigoPostal>"
    Then el mensaje de correcto debe ser "<mensajeEsperado>"

  Examples:
    | usuario       | password     | nombre | apellido | codigoPostal | mensajeEsperado          |
    | standard_user | secret_sauce | Yoder  | Omar     | 12345        | THANK YOU FOR YOUR ORDER |
    | standard_user | secret_sauce | Laura  | Gómez    | 54321        | THANK YOU FOR YOUR ORDER |
    | standard_user | secret_sauce | Pedro  | Muñoz    | 11223        | THANK YOU FOR YOUR ORDER |
    | standard_user | secret_sauce | Andres | Perez    | 11223        | THANK YOU FOR YOUR ORDER |
    | standard_user | secret_sauce | Jorge  | Ruiz     | 11223        | THANK YOU FOR YOUR ORDER |
    | standard_user | secret_sauce | Daniel | Calero   | 11223        | THANK YOU FOR YOUR ORDER |

  @IA @compraSaucesCatalogoIA
  Scenario: Completar una compra satisfactoriamente con catalogo IA
    Given se carga el catalogo IA "compra-saucedemo"
    And el usuario se logea con credenciales del catalogo IA activo
    When el usuario agrega dos productos al carrito
    And procede al checkout de los productos agregados al carrito
    And completa el formulario de compra con datos IA del catalogo activo
    Then el mensaje de correcto del catalogo IA activo debe ser visible
