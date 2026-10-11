// TV Link firmware - Arduino Uno/Nano + IR LED (D3) + optional IR receiver (D11)
// Requires library: IRremote 4.x (Library Manager -> "IRremote" by shirriff/z3t0/ArminJo)
// Serial protocol, 115200 baud, newline terminated:
//   PING                              -> PONG
//   SEND <PROTO> <addr> <cmd> [reps]  -> OK | ERR <reason>     (PROTO: NEC SAMSUNG LG SONY RC5)
//   LEARN                             -> CODE <PROTO> <addr> <cmd> | TIMEOUT
#include <Arduino.h>
#include <IRremote.hpp>

#define IR_SEND_PIN 3
#define IR_RECV_PIN 11
static const unsigned long LEARN_TIMEOUT_MS = 10000UL;

static char buf[64];
static uint8_t len = 0;

static void doSend(char *ctx) {
  char *proto = strtok_r(NULL, " ", &ctx);
  char *a = strtok_r(NULL, " ", &ctx);
  char *c = strtok_r(NULL, " ", &ctx);
  char *r = strtok_r(NULL, " ", &ctx);
  if (!proto || !a || !c) { Serial.println(F("ERR usage")); return; }
  uint16_t addr = (uint16_t)strtoul(a, NULL, 0);
  uint16_t cmd = (uint16_t)strtoul(c, NULL, 0);
  int8_t reps = r ? (int8_t)atoi(r) : 0;
  if (reps < 0 || reps > 10) reps = 0;

  if (!strcasecmp(proto, "NEC")) IrSender.sendNEC(addr, cmd, reps);
  else if (!strcasecmp(proto, "SAMSUNG")) IrSender.sendSamsung(addr, cmd, reps);
  else if (!strcasecmp(proto, "LG")) IrSender.sendLG(addr, cmd, reps);
  else if (!strcasecmp(proto, "SONY")) IrSender.sendSony(addr, cmd, reps < 2 ? 2 : reps, 12);
  else if (!strcasecmp(proto, "RC5")) IrSender.sendRC5(addr, cmd, reps);
  else { Serial.println(F("ERR protocol")); return; }
  Serial.println(F("OK"));
}

static void doLearn() {
  IrReceiver.resume();
  unsigned long start = millis();
  while (millis() - start < LEARN_TIMEOUT_MS) {
    if (IrReceiver.decode()) {
      IRData &d = IrReceiver.decodedIRData;
      bool usable = d.protocol != UNKNOWN && !(d.flags & IRDATA_FLAGS_IS_REPEAT);
      if (usable) {
        Serial.print(F("CODE "));
        Serial.print(IrReceiver.getProtocolString());
        Serial.print(F(" 0x")); Serial.print(d.address, HEX);
        Serial.print(F(" 0x")); Serial.println(d.command, HEX);
        IrReceiver.resume();
        return;
      }
      IrReceiver.resume();
    }
  }
  Serial.println(F("TIMEOUT"));
}

static void handle(char *line) {
  char *ctx = NULL;
  char *cmd = strtok_r(line, " ", &ctx);
  if (!cmd) return;
  if (!strcasecmp(cmd, "PING")) Serial.println(F("PONG"));
  else if (!strcasecmp(cmd, "SEND")) doSend(ctx);
  else if (!strcasecmp(cmd, "LEARN")) doLearn();
  else Serial.println(F("ERR unknown"));
}

void setup() {
  Serial.begin(115200);
  IrSender.begin(IR_SEND_PIN);
  IrReceiver.begin(IR_RECV_PIN, DISABLE_LED_FEEDBACK);
  Serial.println(F("READY"));
}

void loop() {
  while (Serial.available()) {
    char ch = (char)Serial.read();
    if (ch == '\r') continue;
    if (ch == '\n') { buf[len] = 0; handle(buf); len = 0; }
    else if (len < sizeof(buf) - 1) buf[len++] = ch;
    else len = 0; // overflow: drop line
  }
}
