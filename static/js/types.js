class TypedJSON {
    static #types = new Map()

    static parse(string) {
        JSON.parse(string, (key, value) => {
            return value.hasOwnProperty('__type__') ? this.#types.get(value.__type__).fromJSON(value) : value;
        })
    }

    static register(name, type) {
        this.#types.set(name, type)
    }
}

class Question {
    #number
    #type
    #text
    #answers


    constructor(number, type, title, answers) {
        this.#number = number;
        this.#type = type;
        this.#text = title;
        this.#answers = answers.slice();
    }

    toJSON() {
        return {
            __type__: 'Question',
            number: this.#number,
            type: this.#type,
            title: this.#text,
            answers: this.#answers
        }
    }

    static fromJSON(data) {
        return new Question(data.number, data.type, data.title, data.answers);
    }

    get type() {
        return this.#type;
    }

    get text() {
        return this.#text;
    }

    get answers() {
        return this.#answers;
    }
}

TypedJSON.register(Question);