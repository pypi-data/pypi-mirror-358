from bioamla.ast import wav_ast_inference
 
if __name__ == '__main__':
  import sys
  prediction = wav_ast_inference(sys.argv[1], sys.argv[2], int(sys.argv[3]))
  print(prediction)