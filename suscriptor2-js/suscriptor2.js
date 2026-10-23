/**
 * Suscriptor 2 (JavaScript / Node.js)
 */
const amqp = require("amqplib");
const fs = require("fs");
const path = require("path");

const RABBIT_URL = "amqp://guest:guest@localhost:5672";
const EXCHANGE = "ropa_exchange";
const MARCA = "nike"; // routing key a la que se suscribe
const COLA = "cola_nike";
const ARCHIVO = path.join(__dirname, "pedidos.txt");

async function main() {
  const conexion = await amqp.connect(RABBIT_URL);
  const canal = await conexion.createChannel();

  // Exchange direct + cola propia enlazada SOLO con la routing key "nike"
  await canal.assertExchange(EXCHANGE, "direct", { durable: true });
  await canal.assertQueue(COLA, { durable: true });
  await canal.bindQueue(COLA, EXCHANGE, MARCA);

  console.log(`[Suscriptor 2 - JS] Suscrito a '${MARCA}' (cola '${COLA}'). CTRL+C para salir.`);

  canal.consume(COLA, (msg) => {
    if (!msg) return;
    const cuerpo = msg.content.toString("utf8");
    try {
      const pedido = JSON.parse(cuerpo); // valida que sea JSON
      const linea = JSON.stringify({ marca: pedido.marca, producto: pedido.producto, cantidad: pedido.cantidad });
      fs.appendFileSync(ARCHIVO, linea + "\n", "utf8");
      console.log("  Escrito en TXT ->", linea);
      canal.ack(msg);
    } catch (err) {
      console.error("  Mensaje inválido descartado:", cuerpo);
      canal.nack(msg, false, false);
    }
  });

  process.on("SIGINT", async () => {
    await canal.close();
    await conexion.close();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error("No se pudo conectar a RabbitMQ:", err.message);
  process.exit(1);
});
