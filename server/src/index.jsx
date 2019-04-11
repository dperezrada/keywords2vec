import React from 'react'
import ReactDOM from 'react-dom'

import axios from 'axios'

console.clear();

const SuggestTerm = ({terms, selectElement}) => {
  return (
    <div className="select is-multiple is-fullwidth">
      <select multiple size="8" style={{position: "absolute", zIndex: 2}}>
        {
          terms.map(
            (term, index) => {
              return <option
                value={term} key={"sug-" + index}
                onClick={(ev) => {selectElement(ev.target.value)}}

              >{term}</option>
            }
          )
        }
      </select>
    </div>
  )
}

class KeywordInput extends React.Component{
  constructor(props){
    // Pass props to parent class
    super(props)
    this.props = props
    this.suggestionTimeout = null 
    this.state = {
      suggestions: [],
      term: "",
      showSuggestions: false
    }
  }
  updateSuggestion(term) {
    if(term && term.length >= 2){

      clearTimeout(this.suggestionTimeout);
      this.suggestionTimeout = setTimeout(
        () => {
          this.setState(
            {
              suggestions: this.props.suggestTerms(this.state.term.split(",").pop()),
              showSuggestions: true
            }
          )
        }, 300
      );
    }
  }
  render(){
    return (
      <div>
        <input 
          className="input is-primary positive"
          type="text" placeholder="Positive keywords"
          value={this.state.term}
          onChange={ev => {
            this.props.updateValue(ev.target.value)
            this.setState({
              term: ev.target.value,
              showSuggestions: false
            })
            this.updateSuggestion(ev.target.value)
          }}
        />
        {
          this.state.showSuggestions && 
          <SuggestTerm terms={this.state.suggestions} selectElement={
            (term) => {
              let newtermSplit = this.state.term.split(",")
              newtermSplit[newtermSplit.length - 1] = term
              this.setState({
                showSuggestions: false,
                term: newtermSplit.join(",")
              })
              this.props.updateValue(term)
            }
          }/>
        }
      </div>
    )
  }
}

class SearchForm extends React.Component{
  constructor(props){
    // Pass props to parent class
    super(props)
    this.props = props
    this.state = {
      positive: "",
      negative: "",
      size: 50

    }
  }
  componentDidMount(){
    
  }
  render () {
    return <div className="section">
      <h1>Explore the word2vec vectors</h1>
      <div className="field">
        <div className="control">
          <span>Positive keyword.</span>
          <span style={{color: "#CCC", fontSize: "0.8em", marginLeft: "5px"}}>Example: heart failure</span>
          <KeywordInput suggestTerms={this.props.suggestTerms} updateValue={(v) => {this.setState({positive: v})}} />
        </div>
      </div>
      <div className="field">
        Negative keyword
        <div className="control">
          <KeywordInput suggestTerms={this.props.suggestTerms} updateValue={(v) => {this.setState({negative: v})}} />
        </div>
      </div>
      <div className="field">
        Number of results
        <div className="control">
          <input
            className="input is-primary size" value={this.state.size}
            type="text" placeholder="Total results"
            onChange={ev => {this.setState({size: ev.target.value})}}
          />
        </div>
      </div>
      <div className="error-messages"></div>
      <div><a className={"button keywords-btn" + (this.props.isLoading ? " is-loading":"")} onClick={() => {
        this.props.search(this.state.positive, this.state.negative, this.state.size)
      }}>Get keywords</a></div>
    </div>
  }
}

const SimilarsComp = ({similars}) => {
  return (
    <div style={{marginTop: "20px"}} className="results columns is-gapless is-multiline is-mobile">
      {
        similars.map((similar, index) =>
          <div className="card column is-half" key={"sim-" + index}>
            <div className="card-content">
              <p className="title">{similar[0]}</p>
            </div>
          </div>
        )
      }
    </div>
  )
}

let findTerms = function(all_keywords, term, limit=30){
  let returnElements = []
  let totalFound = 0
  for (var i = 0, len = all_keywords.length; i < len; i++){
    if (all_keywords[i].indexOf(term) == 0){
      returnElements.push(all_keywords[i])
      totalFound++; 
      if(totalFound >= limit){
        return returnElements
      }
    }
  }
  return returnElements
}

class VectorsApp extends React.Component{
  constructor(props){
    // Pass props to parent class
    super(props);
    // Set initial state
    this.state = {
      positive: "",
      negative: "",
      keywords: [],
      similars: [],
      size: 200,
      isLoading: true 
    }
  }
  componentDidMount(){
    axios.get("./keywords/all")
      .then((res) => {
        this.setState({
          keywords: res.data.sort(),
          isLoading: false
        })
        window.keywords = res.data.sort()
      }
    )
  }
  search(positive, negative, size){
    // Update data
    var targetUrl = "./keywords/similars?"
    targetUrl += "positive=" + positive
    targetUrl += "&negative=" + negative
    targetUrl += "&size=" + size

    this.setState({isLoading: true})
    axios.get(targetUrl)
      .then((res) => {
        this.setState({similars: res.data, isLoading: false})
      });
  }

  suggestTerms(term){
    return findTerms(this.state.keywords, term)
  }
  render(){
    // Render JSX
    return (
      <div>
        <SearchForm search={this.search.bind(this)} suggestTerms={this.suggestTerms.bind(this)} isLoading={this.state.isLoading}/>
        <SimilarsComp similars={this.state.similars}/>
      </div>
    );
  }
}

ReactDOM.render(<VectorsApp />, document.getElementById('container'));
