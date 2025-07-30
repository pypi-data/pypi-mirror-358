from palang import use as palang

# tell_joke = palang.import_program("hello::tell_joke").with_model("llama3")

greet = palang.import_program("hello::greet").with_model("llama3")
greet = palang.hello.greet.with_model("llama3")

def main():
    greeting = greet()
    print(greeting)
    
    # joke = tell_joke()
    # print(joke)

if __name__ == "__main__":
    main()
